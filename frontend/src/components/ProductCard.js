import React, { useState } from 'react';

const ProductCard = ({ product, onAction }) => {
  const [imageError, setImageError] = useState(false);

  const handleImageError = () => {
    setImageError(true);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const renderRating = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="star full">★</span>);
    }

    if (hasHalfStar) {
      stars.push(<span key="half" className="star half">★</span>);
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="star empty">☆</span>);
    }

    return stars;
  };

  const getStockStatus = (quantity) => {
    if (quantity === 0) return { text: 'Out of Stock', class: 'out-of-stock' };
    if (quantity < 10) return { text: 'Low Stock', class: 'low-stock' };
    return { text: 'In Stock', class: 'in-stock' };
  };

  const stockStatus = getStockStatus(product.stock_quantity);

  return (
    <div className="product-card">
      <div className="product-image">
        {!imageError ? (
          <img
            src={product.image_url}
            alt={product.name}
            onError={handleImageError}
          />
        ) : (
          <div className="image-placeholder">
            <span>📱</span>
          </div>
        )}
        <div className="product-badge">
          {product.category.replace('_', ' ').toUpperCase()}
        </div>
      </div>

      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-brand">{product.brand}</p>
        
        <div className="product-rating">
          {renderRating(product.rating)}
          <span className="rating-value">({product.rating})</span>
        </div>

        <p className="product-description">
          {product.description.length > 100
            ? `${product.description.substring(0, 100)}...`
            : product.description}
        </p>

        <div className="product-price">
          <span className="price">{formatPrice(product.price)}</span>
        </div>

        <div className={`stock-status ${stockStatus.class}`}>
          {stockStatus.text}
        </div>

        <div className="product-actions">
          <button
            onClick={() => onAction(product, 'view')}
            className="action-btn view-btn"
          >
            View Details
          </button>
          <button
            onClick={() => onAction(product, 'compare')}
            className="action-btn compare-btn"
          >
            Compare
          </button>
          
        </div>
      </div>
    </div>
  );
};

export default ProductCard;