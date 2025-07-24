import React from 'react';

const EnvironmentDebug = () => {
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  const stripeKey = process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY;

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: '#000', 
      color: '#fff', 
      padding: '10px', 
      borderRadius: '5px',
      fontSize: '12px',
      zIndex: 9999,
      maxWidth: '300px'
    }}>
      <h4>Environment Debug</h4>
      <p><strong>Backend URL:</strong> {backendUrl || 'UNDEFINED'}</p>
      <p><strong>Stripe Key:</strong> {stripeKey ? `${stripeKey.substring(0, 20)}...` : 'UNDEFINED'}</p>
      <p><strong>Full Payment URL:</strong> {backendUrl}/api/create-payment-intent</p>
    </div>
  );
};

export default EnvironmentDebug;