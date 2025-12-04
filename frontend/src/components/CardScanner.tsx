import { useRef, useState } from 'react';
import { cardApi } from '../services/api';

function CardScanner() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsScanning(true);
    setMessage('');

    try {
      const result = await cardApi.scanCard(file);
      setMessage(`Success: ${result.message}`);
      // TODO: Refresh card list or add new card to state
    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Failed to scan card'}`);
    } finally {
      setIsScanning(false);
    }
  };

  const handleScanClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="card-scanner">
      <h2>Scan a Card</h2>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      <button
        onClick={handleScanClick}
        disabled={isScanning}
        className="scan-button"
      >
        {isScanning ? 'Scanning...' : 'Take Photo / Upload Image'}
      </button>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default CardScanner;
