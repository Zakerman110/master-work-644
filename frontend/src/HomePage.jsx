import React, { useState, useEffect } from "react";
import apiClient from "./axiosConfig";

const HomePage = () => {
    const [searchTerm, setSearchTerm] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [reviewsBySource, setReviewsBySource] = useState([]);
    const [error, setError] = useState("");
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("");
    const [currentPage, setCurrentPage] = useState(1); // Track the current page
    const [totalPages, setTotalPages] = useState(0); // Track the total pages

    // Fetch categories when the component mounts
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

    const handleSearch = async (page = 1) => {
        try {
            setError("");
            setSuggestions([]);
            setSelectedProduct(null);

            const response = await apiClient.get(`/api/suggestions/`, {
                params: {
                    query: searchTerm,
                    category_id: selectedCategory,
                    page: page, // Send the current page as a query parameter
                },
            });

            setSuggestions(response.data.results); // Paginated results
            setTotalPages(Math.ceil(response.data.count / 21)); // Assuming default page size of 10
            setCurrentPage(page); // Update current page
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

            const productResponse = await apiClient.get(`/api/product/`, {
                params: { name: productId }, // Assuming the API accepts the product name
            });

            const product = productResponse.data;
            setSelectedProduct(product);

            // Fetch reviews for the selected product
            const reviewsResponse = await apiClient.get(`/api/product/${product.id}/reviews/`);
            setReviewsBySource(reviewsResponse.data);
        } catch (err) {
            setError("Error fetching product details or reviews.");
            console.error(err);
        }
    };

    const handlePageChange = (page) => {
        handleSearch(page); // Trigger search with the new page
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
                        onClick={() => handleSearch(1)} // Reset to page 1 on new search
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
                                onClick={() => handleSelectProduct(suggestion.name)} // Pass name or ID
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
                                    <li key={i} className="mb-2">
                                        <strong>{review.rating} Stars:</strong> {review.text}
                                        <span
                                            className="ml-2 px-2 py-1 text-sm rounded-full"
                                            style={{
                                                backgroundColor:
                                                    review.sentiment === "Positive"
                                                        ? "#d4edda"
                                                        : review.sentiment === "Negative"
                                                        ? "#f8d7da"
                                                        : "#fff3cd",
                                                color:
                                                    review.sentiment === "Positive"
                                                        ? "#155724"
                                                        : review.sentiment === "Negative"
                                                        ? "#721c24"
                                                        : "#856404",
                                            }}
                                        >
                                            {review.sentiment}
                                        </span>
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
