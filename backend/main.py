from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import json
from typing import Optional

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_eslint() -> Optional[str]:
    """Try to locate ESLint executable"""
    possible_paths = [
        "eslint",  # Try default path first
        os.path.join(os.environ.get("APPDATA", ""), "npm", "eslint.cmd"),  # Windows
        "/usr/local/bin/eslint",  # macOS/Linux
        "/usr/bin/eslint",
        os.path.expanduser("~/.npm-global/bin/eslint"),
    ]
    
    for path in possible_paths:
        try:
            subprocess.run([path, "--version"], 
                         check=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
            return path
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    return None

def analyze_code(filename: str, content: str) -> dict:
    """Route analysis based on file type"""
    if filename.endswith(('.js', '.jsx')):
        return analyze_js_code(content)
    elif filename.endswith('.py'):
        return analyze_py_code(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

def analyze_js_code(code: str) -> dict:
    """Analyze JavaScript code using ESLint"""
    eslint_path = find_eslint()
    if not eslint_path:
        return basic_js_analysis(code)  # Fallback to basic analysis
    
    try:
        # Write temp file
        with open("temp_analysis.js", "w", encoding="utf-8") as f:
            f.write(code)
        
        # Run ESLint
        result = subprocess.run(
            [eslint_path, "temp_analysis.js", "--format=json"],
            capture_output=True,
            text=True,
            timeout=30  # Prevent hanging
        )
        
        if result.returncode not in [0, 1]:  # 0=no issues, 1=issues found
            raise subprocess.SubprocessError(f"ESLint failed with code {result.returncode}")
        
        issues = json.loads(result.stdout)[0]["messages"] if result.stdout else []
        
        # Calculate score (100 - 5 points per issue, min 0)
        score = max(0, 100 - (len(issues) * 5))
        
        return {
            "overall_score": score,
            "breakdown": {
                "naming": score_metric(issues, ["naming", "case", "name"], 10),
                "modularity": score_metric(issues, ["length", "complexity"], 20),
                "comments": score_metric(issues, ["comment", "doc"], 20),
                "formatting": score_metric(issues, ["format", "indent", "space"], 15),
                "reusability": score_metric(issues, ["dup", "repeat"], 15),
                "best_practices": score_metric(issues, ["practice", "standard"], 20)
            },
            "recommendations": [f"{msg['message']} (Line {msg['line']})" for msg in issues[:5]]
        }
        
    except Exception as e:
        return basic_js_analysis(code)  # Fallback if ESLint fails
    finally:
        if os.path.exists("temp_analysis.js"):
            os.remove("temp_analysis.js")

def score_metric(issues: list, keywords: list, max_score: int) -> int:
    """Calculate sub-score based on relevant issues"""
    relevant_issues = sum(1 for issue in issues)
    if any(kw in issue.get("ruleId", "").lower() for issue in issues for kw in keywords):
      return max(0, max_score - (relevant_issues * 2))

def basic_js_analysis(code: str) -> dict:
    """Fallback JavaScript analysis without ESLint"""
    issues = []
    score = 100  # Start with perfect score
    
    # Basic checks
    if "var " in code:
        issues.append("Use 'const' or 'let' instead of 'var'")
        score -= 5
    
    if "console.log" in code:
        issues.append("Remove debug console.log statements")
        score -= 3
    
    # Check for large functions
    functions = [f for f in code.split("function ") if f.strip()]
    if len(functions) > 0:
        avg_length = sum(len(f) for f in functions) / len(functions)
        if avg_length > 300:
            issues.append("Functions are too long (average {:.0f} chars)".format(avg_length))
            score -= 10
    
    return {
        "overall_score": max(0, score),
        "breakdown": {
            "naming": 6 if "var " in code else 10,
            "modularity": 15 if len(functions) > 5 else 20,
            "comments": 10 if "//" not in code and "/*" not in code else 20,
            "formatting": 15,
            "reusability": 10,
            "best_practices": 15 if "console.log" in code else 20
        },
        "recommendations": issues[:5] or ["Basic analysis completed - install ESLint for more detailed results"]
    }

def analyze_py_code(code: str) -> dict:
    """Analyze Python code using pylint"""
    try:
        with open("temp_analysis.py", "w", encoding="utf-8") as f:
            f.write(code)
        
        result = subprocess.run(
            ["pylint", "temp_analysis.py", "--output-format=json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        issues = json.loads(result.stdout) if result.stdout else []
        
        # Calculate score
        score = max(0, 100 - len(issues))
        
        return {
            "overall_score": score,
            "breakdown": {
                "naming": score_metric(issues, ["naming", "name"], 10),
                "modularity": score_metric(issues, ["length", "complexity"], 20),
                "comments": score_metric(issues, ["docstring", "comment"], 20),
                "formatting": score_metric(issues, ["indent", "whitespace"], 15),
                "reusability": score_metric(issues, ["duplicate", "repeated"], 15),
                "best_practices": score_metric(issues, ["standard", "practice"], 20)
            },
            "recommendations": [f"{msg['message']} (Line {msg['line']})" for msg in issues[:5]]
        }
        
    except Exception as e:
        return {
            "overall_score": 0,
            "breakdown": {k: 0 for k in ["naming", "modularity", "comments", "formatting", "reusability", "best_practices"]},
            "recommendations": [f"Analysis failed: {str(e)}"]
        }
    finally:
        if os.path.exists("temp_analysis.py"):
            os.remove("temp_analysis.py")

@app.post("/analyze-code")
async def analyze_code_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.js', '.jsx', '.py')):
        raise HTTPException(400, detail="Only .js, .jsx, or .py files accepted")
    
    try:
        content = (await file.read()).decode("utf-8")
        return analyze_code(file.filename, content)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)