import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

const rootEl = document.getElementById('root');
if (!rootEl) {
  throw new Error('Root-Element #root fehlt im HTML.');
}
createRoot(rootEl).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
