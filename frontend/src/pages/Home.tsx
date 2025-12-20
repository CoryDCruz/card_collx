import { useState } from 'react';
import CardScanner from '../components/CardScanner';

function Home() {
  const [cards] = useState([]);

  return (
    <div className="home">
      <header>
        <h1>Card Collection Tracker</h1>
        <p>Scan and manage your sports card collection</p>
      </header>

      <main>
        <CardScanner />

        <section className="card-list">
          <h2>Your Collection</h2>
          {cards.length === 0 ? (
            <p>No cards yet. Scan your first card to get started!</p>
          ) : (
            <div className="cards-grid">
              {/* TODO: Map through cards and display them */}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Home;
