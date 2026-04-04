import { useState, useEffect } from 'react';
import CardScanner from '../components/CardScanner';
import { cardApi } from '../services/api';
import type { Card } from '../types/card';

function Home() {
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCards = async () => {
    try {
      setError(null);
      const data = await cardApi.getAllCards();
      setCards(data);
    } catch (err) {
      setError('Failed to load cards. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCards();
  }, []);

  return (
    <div className="home">
      <header>
        <h1>Card Collection Tracker</h1>
        <p>Scan and manage your sports card collection</p>
      </header>

      <main>
        <CardScanner onScanComplete={fetchCards} />

        <section className="card-list">
          <h2>Your Collection ({cards.length})</h2>

          {loading ? (
            <p className="loading-message">Loading your collection...</p>
          ) : error ? (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={fetchCards} className="retry-button">Retry</button>
            </div>
          ) : cards.length === 0 ? (
            <p>No cards yet. Scan your first card to get started!</p>
          ) : (
            <div className="cards-grid">
              {cards.map((card) => (
                <div className="card-item" key={card.id}>
                  {card.image_url && (
                    <img src={card.image_url} alt={card.player_name} />
                  )}
                  <div className="card-info">
                    <h3>{card.player_name}</h3>
                    <p className="card-meta">
                      {[card.year, card.brand].filter(Boolean).join(' ')}
                    </p>
                    {card.set_name && <p className="card-set">{card.set_name}</p>}
                    {card.sport && <p className="card-sport">{card.sport}</p>}
                    {card.condition && (
                      <span className="condition-badge">{card.condition}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Home;
