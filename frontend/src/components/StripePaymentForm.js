import React, { useState } from 'react';
import {
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { stripeAPI } from '../services/api';

const StripePaymentForm = ({ 
  totalAmount, 
  onSuccess, 
  onError, 
  loading = false,
  disabled = false,
  bundles = [],
  workspaceName = '',
  paymentMethod = 'monthly'
}) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [cardError, setCardError] = useState(null);

  const cardStyle = {
    style: {
      base: {
        color: '#ffffff',
        fontFamily: 'Inter, system-ui, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        lineHeight: '24px',
        '::placeholder': {
          color: '#94a3b8'
        }
      },
      invalid: {
        color: '#ef4444',
        iconColor: '#ef4444'
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setCardError(null);

    const cardElement = elements.getElement(CardElement);

    // Create payment method
    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement,
    });

    if (error) {
      console.error('Stripe error:', error);
      setCardError(error.message);
      setIsProcessing(false);
      onError?.(error);
      return;
    }

    console.log('Payment method created:', paymentMethod);
    
    try {
      // Create checkout session via backend
      const checkoutResponse = await stripeAPI.createCheckoutSession({
        bundles: bundles,
        workspace_name: workspaceName,
        payment_method: paymentMethod
      });
      
      if (checkoutResponse.data.success) {
        // If checkout session created successfully, confirm payment
        const confirmResponse = await stripeAPI.confirmPayment({
          paymentMethodId: paymentMethod.id,
          sessionId: checkoutResponse.data.session_id
        });
        
        if (confirmResponse.data.success) {
          onSuccess?.({
            paymentMethodId: paymentMethod.id,
            paymentMethod: paymentMethod,
            sessionId: checkoutResponse.data.session_id
          });
        } else {
          throw new Error(confirmResponse.data.error || 'Payment confirmation failed');
        }
      } else {
        throw new Error(checkoutResponse.data.error || 'Checkout session creation failed');
      }
    } catch (err) {
      console.error('Backend payment processing error:', err);
      setCardError(err.response?.data?.detail || err.message || 'Payment processing failed');
      onError?.(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCardChange = (event) => {
    if (event.error) {
      setCardError(event.error.message);
    } else {
      setCardError(null);
    }
  };

  return (
    <div className="stripe-payment-form">
      <form onSubmit={handleSubmit}>
        <div className="card-input-section">
          <label className="card-label">
            Card Information
          </label>
          <div className="card-element-container">
            <CardElement
              options={cardStyle}
              onChange={handleCardChange}
            />
          </div>
          {cardError && (
            <div className="card-error">
              {cardError}
            </div>
          )}
        </div>

        <div className="payment-security-notice">
          <div className="security-icons">
            🔒 🛡️
          </div>
          <div className="security-text">
            <p>Your payment information is secured with 256-bit SSL encryption</p>
            <p className="powered-by">Powered by Stripe</p>
          </div>
        </div>

        <button
          type="submit"
          disabled={!stripe || isProcessing || loading || disabled}
          className="stripe-submit-button"
        >
          {isProcessing ? (
            <span className="processing-text">
              <span className="spinner"></span>
              Processing...
            </span>
          ) : (
            `Start Free Trial - $${totalAmount}/month after trial`
          )}
        </button>
      </form>
    </div>
  );
};

export default StripePaymentForm;