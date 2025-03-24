import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/analyze-code', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Carbon Crunch</h1>
        <p>Analyze your code quality</p>
        
        <form onSubmit={handleSubmit}>
          <input type="file" onChange={handleFileChange} accept=".js,.jsx,.py" />
          <button type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze Code'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result">
            <h2>Analysis Results</h2>
            <div className="score">
              Overall Score: <span>{result.overall_score}/100</span>
            </div>
            
            <div className="breakdown">
              <h3>Breakdown:</h3>
              <ul>
                <li>Naming Conventions: {result.breakdown.naming}/10</li>
                <li>Function Length/Modularity: {result.breakdown.modularity}/20</li>
                <li>Comments/Documentation: {result.breakdown.comments}/20</li>
                <li>Formatting/Indentation: {result.breakdown.formatting}/15</li>
                <li>Reusability/DRY: {result.breakdown.reusability}/15</li>
                <li>Best Practices: {result.breakdown.best_practices}/20</li>
              </ul>
            </div>
            
            <div className="recommendations">
              <h3>Recommendations:</h3>
              <ul>
                {result.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;