import React, { useState, useEffect } from "react";
import apiClient from "./axiosConfig";

const HomePage = () => {
    const [searchTerm, setSearchTerm] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [reviewsBySource, setReviewsBySource] = useState([]);
    const [metrics, setMetrics] = useState(null);
    const [error, setError] = useState("");
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [userReview, setUserReview] = useState("");
    const [userRating, setUserRating] = useState(0);
    const [filterSentiment, setFilterSentiment] = useState("all");

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await apiClient.get("/api/categories/");
                setCategories(response.data);
            } catch (err) {
                console.error("Error fetching categories:", err);
            }
        };

        fetchCategories();
    }, []);

    const calculateMetrics = (reviews) => {
        let positiveCount = 0;
        let neutralCount = 0;
        let negativeCount = 0;
        let totalRating = 0;
        let totalReviews = 0;

        reviews.forEach((source) => {
            source.reviews.forEach((review) => {
                totalRating += review.rating;
                totalReviews++;
                const sentiment = review.human_sentiment || review.model_sentiment;
                if (sentiment === "Positive") positiveCount++;
                else if (sentiment === "Neutral") neutralCount++;
                else if (sentiment === "Negative") negativeCount++;
            });
        });

        const overallScore = totalReviews > 0 ? (totalRating / totalReviews).toFixed(2) : "N/A";

        return {
            positiveCount,
            neutralCount,
            negativeCount,
            overallScore,
        };
    };

    const markReviewForReview = async (reviewId) => {
        try {
            await apiClient.post(`/api/reviews/${reviewId}/mark-for-review/`);
            alert("Review marked for admin review.");
        } catch (err) {
            console.error("Error marking review for review:", err);
        }
    };

    const handleSearch = async (page = 1) => {
        try {
            setError("");
            setSuggestions([]);
            setSelectedProduct(null);

            const response = await apiClient.get(`/api/suggestions/`, {
                params: {
                    query: searchTerm,
                    category_id: selectedCategory,
                    page: page,
                },
            });

            setSuggestions(response.data.results);
            setTotalPages(Math.ceil(response.data.count / 21));
            setCurrentPage(page);
        } catch (err) {
            setError("Error fetching suggestions.");
            console.error(err);
        }
    };

    const handleSelectProduct = async (productId) => {
        try {
            setError("");
            setSelectedProduct(null);
            setReviewsBySource([]);
            setMetrics(null);

            const productResponse = await apiClient.get(`/api/product/`, {
                params: { name: productId },
            });

            const product = productResponse.data;
            setSelectedProduct(product);

            // Fetch reviews for the selected product
            const reviewsResponse = await apiClient.get(`/api/product/${product.id}/reviews/`);
            setReviewsBySource(reviewsResponse.data);

            // Calculate metrics
            const calculatedMetrics = calculateMetrics(reviewsResponse.data);
            setMetrics(calculatedMetrics);
        } catch (err) {
            setError("Error fetching product details or reviews.");
            console.error(err);
        }
    };

    const handleAddReview = async () => {
        try {
            if (!userReview || userRating <= 0) {
                alert("Please provide a valid comment and rating.");
                return;
            }

            await apiClient.post(`/api/product/${selectedProduct.id}/add-review/`, {
                text: userReview,
                rating: userRating,
            });

            alert("Your review has been submitted!");
            setUserReview("");
            setUserRating(0);

            // Refresh reviews to include the newly added review
            const reviewsResponse = await apiClient.get(`/api/product/${selectedProduct.id}/reviews/`);
            setReviewsBySource(reviewsResponse.data);
        } catch (err) {
            console.error("Error adding review:", err);
            alert("Failed to submit your review.");
        }
    };

    const handlePageChange = (page) => {
        handleSearch(page);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
            <h1 className="text-4xl font-bold text-center mb-8">Пошук продукту</h1>
            <div className="flex flex-col w-full max-w-2xl">
                {/* Search Bar */}
                <div className="flex mb-4">
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Введіть назву продукту..."
                        className="flex-grow p-3 rounded-l-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                        onClick={() => handleSearch(1)}
                        className="p-3 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600"
                    >
                        Пошук
                    </button>
                </div>

                {/* Category Dropdown */}
                <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="mb-4 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">Всі категорії</option>
                    {categories.map((category) => (
                        <option key={category.id} value={category.id}>
                            {category.name}
                        </option>
                    ))}
                </select>
            </div>

            {error && <p className="text-red-500 mt-4">{error}</p>}

            {/* Render Suggestions */}
            {suggestions.length > 0 && (
                <div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
                        {suggestions.map((suggestion) => (
                            <div
                                key={suggestion.id}
                                className={`flex flex-col items-center bg-white shadow-md rounded-lg p-4 cursor-pointer hover:shadow-lg ${
                                    suggestion.is_detailed ? "border-green-500 border-2" : "border-gray-300"
                                }`}
                                onClick={() => handleSelectProduct(suggestion.name)}
                            >
                                <img
                                    src={suggestion.image_url || "placeholder.jpg"}
                                    alt={suggestion.name}
                                    className="w-32 h-32 object-cover mb-4"
                                />
                                <p className="text-center font-medium">{suggestion.name}</p>
                                <span
                                    className={`px-2 py-1 mt-2 rounded text-sm ${
                                        suggestion.is_detailed ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                                    }`}
                                >
                                    {suggestion.is_detailed ? "В системі" : "Потребує скрапінгу"}
                                </span>
                            </div>
                        ))}
                    </div>

                    {/* Pagination */}
                    <div className="flex justify-center items-center mt-4">
                        {Array.from({ length: totalPages }, (_, index) => (
                            <button
                                key={index + 1}
                                onClick={() => handlePageChange(index + 1)}
                                className={`px-4 py-2 mx-1 rounded ${
                                    currentPage === index + 1
                                        ? "bg-blue-500 text-white"
                                        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                                }`}
                            >
                                {index + 1}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Render Selected Product */}
            {selectedProduct && (
                <div className="mt-8 bg-white shadow-md rounded-lg p-6 w-full max-w-2xl">
                    <h2 className="text-2xl font-bold mb-4">{selectedProduct.name}</h2>
                    <img
                        src={selectedProduct.image_url || "placeholder.jpg"}
                        alt={selectedProduct.name}
                        className="w-full max-h-64 object-cover mb-4"
                    />
                    <p className="text-gray-700 mb-4">{selectedProduct.description}</p>

                    {/* Metrics Section */}
                    {metrics && (
                        <div className="mb-6">
                            <h3 className="text-xl font-bold mb-4">Метрики</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <p className="text-gray-700">
                                    <strong>Позитивні відгуки:</strong> {metrics.positiveCount}
                                </p>
                                <p className="text-gray-700">
                                    <strong>Нейтральні відгуки:</strong> {metrics.neutralCount}
                                </p>
                                <p className="text-gray-700">
                                    <strong>Негативні відгуки:</strong> {metrics.negativeCount}
                                </p>
                                <p className="text-gray-700">
                                    <strong>Загальна оцінка:</strong> {metrics.overallScore}
                                </p>
                            </div>
                        </div>
                    )}

                    <h3 className="text-xl font-bold mb-2">Джерела</h3>
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
                    <h3 className="text-xl font-bold mb-2">Відгуки по Джерелам</h3>
                    <div className="mb-4 flex items-center gap-4">
                        <label htmlFor="sentiment-filter" className="font-medium text-gray-700">
                            Фільтрувати за Настроєм:
                        </label>
                        <select
                            id="sentiment-filter"
                            value={filterSentiment}
                            onChange={(e) => setFilterSentiment(e.target.value)}
                            className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="all">Усі</option>
                            <option value="Positive">Позитивні</option>
                            <option value="Neutral">Нейтральні</option>
                            <option value="Negative">Негативні</option>
                        </select>
                    </div>
                    {reviewsBySource.map((sourceReviews, index) => {
                        const filteredReviews = sourceReviews.reviews.filter((review) => {
                            const sentiment = review.human_sentiment || review.model_sentiment;
                            return filterSentiment === "all" || sentiment === filterSentiment;
                        });

                        return (
                            <div key={index} className="mb-8">
                                <h4 className="text-xl font-bold mb-4">{sourceReviews.marketplace}</h4>
                                {filteredReviews.length > 0 ? (
                                    <div className="flex flex-col gap-4">
                                        {filteredReviews.map((review, i) => {
                                            const sentiment = review.human_sentiment || review.model_sentiment;
                                            const isVerified = Boolean(review.human_sentiment);

                                            return (
                                                <div
                                                    key={i}
                                                    className="p-4 bg-white rounded-lg shadow-md border border-gray-200"
                                                >
                                                    <p className="text-gray-800 font-medium mb-2">
                                                        <strong>{review.rating} Stars</strong>
                                                    </p>
                                                    <p className="text-gray-600 text-sm mb-4">{review.text}</p>
                                                    <div className="flex justify-between items-center">
                                                        <div>
                                        <span
                                            className={`px-3 py-1 rounded-full text-sm ${
                                                sentiment === "Positive"
                                                    ? "bg-green-100 text-green-700"
                                                    : sentiment === "Negative"
                                                        ? "bg-red-100 text-red-700"
                                                        : "bg-yellow-100 text-yellow-700"
                                            }`}
                                        >
                                            {sentiment}
                                        </span>
                                                            {isVerified && (
                                                                <span className="ml-2 px-2 py-1 text-sm bg-blue-100 text-blue-700 rounded-full">
                                                Підтверджено
                                            </span>
                                                            )}
                                                        </div>
                                                        {!isVerified && (
                                                            <button
                                                                onClick={() => markReviewForReview(review.id)}
                                                                className="px-3 py-1 text-sm text-white bg-red-500 rounded-lg hover:bg-red-600"
                                                            >
                                                                Позначити для Розгляду
                                                            </button>
                                                        )}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                ) : (
                                    <p className="text-gray-500">Немає відгуків для вибраного настрою.</p>
                                )}
                            </div>
                        );
                    })}
                    <div className="mt-8 bg-white shadow-md rounded-lg p-6 w-full max-w-2xl">
                        <h3 className="text-xl font-bold mb-4">Додати відгук</h3>
                        <textarea
                            value={userReview}
                            onChange={(e) => setUserReview(e.target.value)}
                            placeholder="Напишість свій коментарій..."
                            className="w-full p-3 border border-gray-300 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <div className="flex items-center mb-4">
                            <label className="mr-4 text-lg">Оцінка:</label>
                            <select
                                value={userRating}
                                onChange={(e) => setUserRating(parseFloat(e.target.value))}
                                className="p-2 border border-gray-300 rounded"
                            >
                                <option value={0}>Вибір</option>
                                {[1, 2, 3, 4, 5].map((rating) => (
                                    <option key={rating} value={rating}>
                                        {rating} Star{rating > 1 ? "s" : ""}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <button
                            onClick={handleAddReview}
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            Залишити відгук
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default HomePage;
