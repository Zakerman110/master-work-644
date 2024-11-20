import React, { useState, useEffect } from "react";
import apiClient from "./axiosConfig";

const AdminPanel = () => {
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);

    useEffect(() => {
        fetchReviews(currentPage);
    }, [currentPage]);

    const fetchReviews = async (page = 1) => {
        setLoading(true);
        setError("");
        try {
            const response = await apiClient.get(`/api/admin/reviews/`, {
                params: { page },
            });
            setReviews(response.data.results);
            setTotalPages(Math.ceil(response.data.count / 21));
        } catch (err) {
            setError("Error fetching reviews.");
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
            alert("Review sentiment updated successfully.");
            fetchReviews(currentPage); // Refresh the list
        } catch (err) {
            console.error("Error updating sentiment:", err);
            alert("Failed to update sentiment.");
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
                                    <strong>Відгук:</strong> {review.text}
                                </p>
                                <p>
                                    <strong>Оцінка:</strong> {review.rating}
                                </p>
                                <p>
                                    <strong>Настрій моделі:</strong> {review.model_sentiment}
                                </p>
                                <div>
                                    <strong>Оновлення настрою:</strong>
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
