import { useState, useEffect } from 'react';
import CardScanner from '../components/CardScanner';
import { cardApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { Card, CardCreate } from '../types/card';

function Home() {
  const { user, signOut } = useAuth();
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingCard, setEditingCard] = useState<Card | null>(null);
  const [editForm, setEditForm] = useState<CardCreate>({ player_name: '' });

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

  const handleDelete = async (card: Card) => {
    if (!confirm(`Delete ${card.player_name}? This cannot be undone.`)) return;
    try {
      await cardApi.deleteCard(card.id);
      setCards(prev => prev.filter(c => c.id !== card.id));
    } catch (err) {
      alert('Failed to delete card. Please try again.');
    }
  };

  const handleEditStart = (card: Card) => {
    setEditingCard(card);
    setEditForm({
      player_name: card.player_name,
      year: card.year,
      brand: card.brand,
      card_number: card.card_number,
      set_name: card.set_name,
      sport: card.sport,
      condition: card.condition,
      notes: card.notes,
    });
  };

  const handleEditSave = async () => {
    if (!editingCard) return;
    try {
      const updated = await cardApi.updateCard(editingCard.id, editForm);
      setCards(prev => prev.map(c => c.id === updated.id ? updated : c));
      setEditingCard(null);
    } catch (err) {
      alert('Failed to update card. Please try again.');
    }
  };

  const handleEditCancel = () => {
    setEditingCard(null);
  };

  return (
    <div className="home">
      <header>
        <div className="header-top">
          <h1>Card Collection Tracker</h1>
          <div className="header-user">
            <span className="user-email">{user?.email}</span>
            <button onClick={signOut} className="logout-button">Log Out</button>
          </div>
        </div>
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
                    <div className="card-actions">
                      <button className="edit-button" onClick={() => handleEditStart(card)}>Edit</button>
                      <button className="delete-button" onClick={() => handleDelete(card)}>Delete</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {editingCard && (
        <div className="modal-overlay" onClick={handleEditCancel}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>Edit Card</h2>
            <form onSubmit={e => { e.preventDefault(); handleEditSave(); }}>
              <label>
                Player Name
                <input
                  type="text"
                  value={editForm.player_name}
                  onChange={e => setEditForm({ ...editForm, player_name: e.target.value })}
                  required
                />
              </label>
              <label>
                Year
                <input
                  type="number"
                  value={editForm.year ?? ''}
                  onChange={e => setEditForm({ ...editForm, year: e.target.value ? Number(e.target.value) : undefined })}
                />
              </label>
              <label>
                Brand
                <input
                  type="text"
                  value={editForm.brand ?? ''}
                  onChange={e => setEditForm({ ...editForm, brand: e.target.value || undefined })}
                />
              </label>
              <label>
                Card Number
                <input
                  type="text"
                  value={editForm.card_number ?? ''}
                  onChange={e => setEditForm({ ...editForm, card_number: e.target.value || undefined })}
                />
              </label>
              <label>
                Set Name
                <input
                  type="text"
                  value={editForm.set_name ?? ''}
                  onChange={e => setEditForm({ ...editForm, set_name: e.target.value || undefined })}
                />
              </label>
              <label>
                Sport
                <input
                  type="text"
                  value={editForm.sport ?? ''}
                  onChange={e => setEditForm({ ...editForm, sport: e.target.value || undefined })}
                />
              </label>
              <label>
                Condition
                <select
                  value={editForm.condition ?? ''}
                  onChange={e => setEditForm({ ...editForm, condition: e.target.value || undefined })}
                >
                  <option value="">Not assessed</option>
                  <option value="Mint">Mint</option>
                  <option value="Near Mint">Near Mint</option>
                  <option value="Excellent">Excellent</option>
                  <option value="Good">Good</option>
                  <option value="Fair">Fair</option>
                  <option value="Poor">Poor</option>
                </select>
              </label>
              <label>
                Notes
                <textarea
                  value={editForm.notes ?? ''}
                  onChange={e => setEditForm({ ...editForm, notes: e.target.value || undefined })}
                />
              </label>
              <div className="modal-actions">
                <button type="button" className="cancel-button" onClick={handleEditCancel}>Cancel</button>
                <button type="submit" className="save-button">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Home;
