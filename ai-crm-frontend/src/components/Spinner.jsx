import React from 'react';
import './Spinner.css';

const Spinner = ({ size = 'medium', message = 'Loading...' }) => {
  return (
    <div className="spinner-container">
      <div className={`spinner ${size}`}></div>
      {message && <div className="spinner-message">{message}</div>}
    </div>
  );
};

export default Spinner;
