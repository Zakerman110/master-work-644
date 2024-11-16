import React, { useState } from 'react';
import apiClient from './axiosConfig';

const HomePage = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [reviewsBySource, setReviewsBySource] = useState([]);
    const [error, setError] = useState('');

    const handleSearch = async () => {
        try {
            setError('');
            setSuggestions([]);
            setSelectedProduct(null);

            const response = await apiClient.get(`/api/suggestions/`, {
                params: { query: searchTerm },
            });

            setSuggestions(response.data);
        } catch (err) {
            setError('Error fetching suggestions.');
            console.error(err);
        }
    };

    const handleSelectProduct = async (productId) => {
        try {
            setError('');
            setSelectedProduct(null);
            setReviewsBySource([]);

            const productResponse = await apiClient.get(`/api/product/`, {
                params: { name: productId }, // Assuming the API accepts the product name
            });

            const product = productResponse.data;
            setSelectedProduct(product);

            // Fetch reviews for the selected product
            const reviewsResponse = await apiClient.get(`/api/product/${product.id}/reviews/`);
            setReviewsBySource(reviewsResponse.data);
        } catch (err) {
            setError('Error fetching product details or reviews.');
            console.error(err);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
            <h1 className="text-4xl font-bold text-center mb-8">Search for a Product</h1>
            <div className="flex w-full max-w-2xl">
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Type product name..."
                    className="flex-grow p-3 rounded-l-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    onClick={handleSearch}
                    className="p-3 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600"
                >
                    Search
                </button>
            </div>

            {error && <p className="text-red-500 mt-4">{error}</p>}

            {/* Render Suggestions */}
            {suggestions.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
                    {suggestions.map((suggestion) => (
                        <div
                            key={suggestion.id}
                            className="flex flex-col items-center bg-white shadow-md rounded-lg p-4 cursor-pointer hover:shadow-lg"
                            onClick={() => handleSelectProduct(suggestion.name)} // Pass name or ID
                        >
                            <img
                                src={suggestion.image_url || 'placeholder.jpg'}
                                alt={suggestion.name}
                                className="w-32 h-32 object-cover mb-4"
                            />
                            <p className="text-center font-medium">{suggestion.name}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Render Selected Product */}
            {selectedProduct && (
                <div className="mt-8 bg-white shadow-md rounded-lg p-6 w-full max-w-2xl">
                    <h2 className="text-2xl font-bold mb-4">{selectedProduct.name}</h2>
                    <img
                        src={selectedProduct.image_url || 'placeholder.jpg'}
                        alt={selectedProduct.name}
                        className="w-full max-h-64 object-cover mb-4"
                    />
                    <p className="text-gray-700 mb-4">{selectedProduct.description}</p>
                    <h3 className="text-xl font-bold mb-2">Sources</h3>
                    <ul className="list-disc list-inside mb-4">
                        {selectedProduct.sources.map((source) => (
                            <li key={source.marketplace}>
                                <a
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-500 hover:underline"
                                >
                                    {source.marketplace} - {source.price}
                                </a>
                            </li>
                        ))}
                    </ul>
                    <h3 className="text-xl font-bold mb-2">Reviews by Source</h3>
                    {reviewsBySource.map((sourceReviews, index) => (
                        <div key={index} className="mb-4">
                            <h4 className="text-lg font-bold mb-2">{sourceReviews.marketplace}</h4>
                            <ul className="list-disc list-inside">
                                {sourceReviews.reviews.map((review, i) => (
                                    <li key={i}>
                                        <strong>{review.rating} Stars:</strong> {review.text}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default HomePage;
