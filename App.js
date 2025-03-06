import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [tweet, setTweet] = useState(null);
  const [error, setError] = useState(null);

  // Function to fetch the latest tweet from the Flask back end.
  const fetchLatestTweet = async () => {
    try {
      // Including credentials so that the session cookie is sent.
      const response = await fetch('http://localhost:5000/latest_tweet', { credentials: 'include' });
      if (!response.ok) {
        throw new Error('Could not fetch tweet. Please sign in.');
      }
      const data = await response.json();
      setTweet(data);
    } catch (err) {
      setError(err.message);
    }
  };

  // Attempt to fetch the tweet on component mount.
  useEffect(() => {
    fetchLatestTweet();
  }, []);

  // Handle the sign-in button click by redirecting to the Flask endpoint.
  const handleSignIn = () => {
    window.location.href = 'http://localhost:5000';
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Twitter to Bluesky Cross-Poster</h1>
      </header>
      <main>
        {error ? (
          <div className="message">
            <p>{error}</p>
            <button className="sign-in-btn" onClick={handleSignIn}>
              Sign in with Twitter
            </button>
          </div>
        ) : tweet ? (
          <div className="tweet-container">
            <h2>Your Latest Tweet</h2>
            <p>{tweet.full_text}</p>
          </div>
        ) : (
          <div className="loading">
            <p>Loading your latest tweet...</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
