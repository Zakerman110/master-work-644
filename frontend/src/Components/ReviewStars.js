import React from 'react';

const getStarText = (rating) => {
    const roundedRating = Math.round(rating);
    if (roundedRating === 1) {
        return 'Зірка'; // Singular
    } else if (roundedRating > 1 && roundedRating < 5) {
        return 'Зірки'; // Few
    } else {
        return 'Зірок'; // Many
    }
};

const ReviewStars = ({ rating }) => {
    return (
        <p className="text-gray-800 font-medium mb-2">
            <strong>{rating} {getStarText(rating)}</strong>
        </p>
    );
};

export default ReviewStars;
