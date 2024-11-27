import React, { useState, useEffect } from "react";
import apiClient from "./axiosConfig";
import { toast } from 'react-toastify';

const AdminPanel = () => {
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [reviewMode, setReviewMode] = useState("marked"); // Default mode is "marked"
    const [confidenceThreshold, setConfidenceThreshold] = useState(0.6); // Default threshold


    useEffect(() => {
        fetchReviews(currentPage);
    }, [currentPage]);

    const fetchReviews = async (page = 1) => {
        setLoading(true);
        setError("");
        try {
            const response = await apiClient.get(`/api/admin/reviews/`, {
                params: {
                    page,
                    mode: reviewMode,
                    confidence_threshold: reviewMode === "low_confidence" ? confidenceThreshold : undefined,
                },
            });
            setReviews(response.data.results);
            setTotalPages(Math.ceil(response.data.count / 21));
        } catch (err) {
            setError("Не вдалося отримати відгуки.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSentimentUpdate = async (reviewId, sentiment) => {
        try {
            await apiClient.post(`/api/admin/reviews/${reviewId}/update-sentiment/`, {
                human_sentiment: sentiment,
            });
            toast.success("Відгуки успішно оновлено.");
            fetchReviews(currentPage); // Refresh the list
        } catch (err) {
            console.error("Error updating sentiment:", err);
            toast.error("Не вдалося оновити відгук.");
        }
    };

    const handlePageChange = (page) => {
        setCurrentPage(page);
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4">
            <h1 className="text-4xl font-bold text-center mb-8">Панель Адміна - Перегляд Відгуків</h1>

            {loading && <p>Завантаження відгуків...</p>}
            {error && <p className="text-red-500">{error}</p>}

            <div className="flex items-center justify-between mb-4">
                <div>
                    <button
                        onClick={() => {
                            setReviewMode("marked");
                            setCurrentPage(1);
                            fetchReviews(1);
                        }}
                        className={`px-4 py-2 mr-2 rounded text-white ${
                            reviewMode === "marked" ? "bg-blue-500" : "bg-gray-300 hover:bg-gray-400"
                        }`}
                    >
                        Marked for Review
                    </button>
                    <button
                        onClick={() => {
                            setReviewMode("low_confidence");
                            setCurrentPage(1);
                            fetchReviews(1);
                        }}
                        className={`px-4 py-2 rounded text-white ${
                            reviewMode === "low_confidence" ? "bg-blue-500" : "bg-gray-300 hover:bg-gray-400"
                        }`}
                    >
                        Low Confidence
                    </button>
                </div>

                {reviewMode === "low_confidence" && (
                    <div className="flex items-center">
                        <label className="mr-2 text-gray-700">Confidence Threshold:</label>
                        <input
                            type="number"
                            value={confidenceThreshold}
                            onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                            step="0.1"
                            min="0"
                            max="1"
                            className="w-20 p-2 border border-gray-300 rounded"
                        />
                        <button
                            onClick={() => fetchReviews(1)}
                            className="ml-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                        >
                            Apply
                        </button>
                    </div>
                )}
            </div>
            
            {!loading && reviews.length === 0 && <p>Ніякі відгуки не потребують розгляду.</p>}

            {reviews.length > 0 && (
                <div>
                    <div className="grid grid-cols-1 gap-4">
                        {reviews.map((review) => (
                            <div
                                key={review.id}
                                className="bg-white shadow-md rounded-lg p-4 flex flex-col gap-4"
                            >
                                <p>
                                    <strong>Review:</strong> {review.text}
                                </p>
                                <p>
                                    <strong>Rating:</strong> {review.rating}
                                </p>
                                <p>
                                    <strong>Model Sentiment:</strong> {review.model_sentiment}
                                </p>
                                {reviewMode === "low_confidence" && (
                                    <p>
                                        <strong>Confidence:</strong> {review.confidence.toFixed(2)}
                                    </p>
                                )}
                                <div>
                                    <strong>Update Sentiment:</strong>
                                    <div className="flex gap-2 mt-2">
                                        {["Positive", "Neutral", "Negative"].map((sentiment) => (
                                            <button
                                                key={sentiment}
                                                onClick={() => handleSentimentUpdate(review.id, sentiment)}
                                                className={`px-4 py-2 rounded text-white ${
                                                    sentiment === "Positive"
                                                        ? "bg-green-500 hover:bg-green-600"
                                                        : sentiment === "Neutral"
                                                            ? "bg-yellow-500 hover:bg-yellow-600"
                                                            : "bg-red-500 hover:bg-red-600"
                                                }`}
                                            >
                                                {sentiment}
                                            </button>
                                        ))}
                                    </div>
                                </div>
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
        </div>
    );
};

export default AdminPanel;
