import React, {useState, useEffect, useContext} from "react";
import { useParams, useNavigate } from "react-router-dom";
import apiClient from "./axiosConfig";
import {AuthContext} from "./AuthContext";
import ReviewStars from "./Components/ReviewStars";
import { toast } from 'react-toastify';

const ProductDetails = () => {
    const { productId } = useParams();
    const [product, setProduct] = useState(null);
    const [reviewsBySource, setReviewsBySource] = useState([]);
    const [metrics, setMetrics] = useState(null);
    const [error, setError] = useState("");
    const [userReview, setUserReview] = useState("");
    const [userRating, setUserRating] = useState(0);
    const [filterSentiment, setFilterSentiment] = useState("all");
    const { user, logout } = useContext(AuthContext);

    const navigate = useNavigate();

    useEffect(() => {
        const fetchProductDetails = async () => {
            try {
                const productResponse = await apiClient.get(`/api/product/`, { params: { productId: productId } });
                setProduct(productResponse.data);

                const reviewsResponse = await apiClient.get(`/api/product/${productResponse.data.id}/reviews/`);
                setReviewsBySource(reviewsResponse.data);

                // Calculate metrics
                const positiveCount = reviewsResponse.data.reduce(
                    (acc, source) => acc + source.reviews.filter(r => r.model_sentiment === "Positive").length,
                    0
                );
                const neutralCount = reviewsResponse.data.reduce(
                    (acc, source) => acc + source.reviews.filter(r => r.model_sentiment === "Neutral").length,
                    0
                );
                const negativeCount = reviewsResponse.data.reduce(
                    (acc, source) => acc + source.reviews.filter(r => r.model_sentiment === "Negative").length,
                    0
                );

                const totalRating = reviewsResponse.data.reduce(
                    (acc, source) => acc + source.reviews.reduce((sum, r) => sum + r.rating, 0),
                    0
                );

                const totalReviews = reviewsResponse.data.reduce(
                    (acc, source) => acc + source.reviews.length,
                    0
                );

                setMetrics({
                    positiveCount,
                    neutralCount,
                    negativeCount,
                    overallScore: totalReviews > 0 ? (totalRating / totalReviews).toFixed(2) : "N/A",
                });
            } catch (err) {
                setError("Помилка при отриманні інформації про товар або відгуків.");
                console.error(err);
            }
        };

        fetchProductDetails();
    }, [productId]);

    const handleAddReview = async () => {
        try {
            if (!userReview || userRating <= 0) {
                toast.error("Будь ласка, надайте коментар та оцінку.");
                return;
            }

            await apiClient.post(`/api/product/${product.id}/add-review/`, {
                text: userReview,
                rating: userRating,
            });

            toast.success("Ваш відгук було надіслано!");
            setUserReview("");
            setUserRating(0);

            // Refresh reviews to include the newly added review
            const reviewsResponse = await apiClient.get(`/api/product/${product.id}/reviews/`);
            setReviewsBySource(reviewsResponse.data);
        } catch (err) {
            console.error("Error adding review:", err);
            toast.error("Не вдалося надіслати ваш відгук.");
        }
    };

    const markReviewForReview = async (reviewId) => {
        try {
            await apiClient.post(`/api/reviews/${reviewId}/mark-for-review/`);
            toast.success("Відгук позначено для перегляду адміністратором.");
        } catch (err) {
            console.error("Error marking review for review:", err);
            toast.error("Не вдалося позначити відгук для перегляду.");
        }
    };

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
            <button onClick={() => navigate(-1)} className="mb-4 p-2 bg-gray-200 hover:bg-gray-300 rounded">
                Повернутися
            </button>
            {product ? (
                <div className="mt-8 bg-white shadow-md rounded-lg p-6 w-full max-w-2xl">
                    <h2 className="text-2xl font-bold mb-4">{product.name}</h2>
                    <img
                        src={product.image_url || "placeholder.jpg"}
                        alt={product.name}
                        className="w-full max-h-64 object-contain mb-4"
                    />
                    <p className="text-gray-700 mb-4">{product.description}</p>

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
                        {product.sources.map((source) => (
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
                                                    <ReviewStars rating={review.rating} />
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
                                                        {!isVerified && user && (
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
                    {user &&
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
                    }
                </div>
            ) : (
                <p>Завантаження...</p>
            )}
        </div>
    );
};

export default ProductDetails;
