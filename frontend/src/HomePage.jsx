import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "./axiosConfig";
import { SearchContext } from "./SearchContext";

const HomePage = () => {
    const {
        searchTerm,
        setSearchTerm,
        searchResults,
        setSearchResults,
        selectedCategory,
        setSelectedCategory,
    } = useContext(SearchContext);

    const [error, setError] = useState("");
    const [categories, setCategories] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [sortBy, setSortBy] = useState(""); // State for sorting
    const navigate = useNavigate();

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
            const response = await apiClient.get(`/api/suggestions/`, {
                params: {
                    query: searchTerm,
                    category_id: selectedCategory,
                    page,
                    sort_by: sortBy,
                },
            });

            setSearchResults(response.data.results);
            setTotalPages(Math.ceil(response.data.count / 21));
            setCurrentPage(page);
        } catch (err) {
            setError("Error fetching suggestions.");
            console.error(err);
        }
    };

    const handleSelectProduct = (productId) => {
        navigate(`/product/${productId}`);
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

                {/* Sort Dropdown */}
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="mb-4 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">Сортувати за</option>
                    <option value="-is_detailed">Деталізовані спочатку</option>
                    <option value="is_detailed">Недеталізовані спочатку</option>
                </select>
            </div>

            {error && <p className="text-red-500 mt-4">{error}</p>}

            {/* Render Suggestions */}
            {searchResults.length > 0 && (
                <div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
                        {searchResults.map((suggestion) => (
                            <div
                                key={suggestion.id}
                                className={`flex flex-col bg-white shadow-md rounded-lg p-4 cursor-pointer hover:shadow-lg ${
                                    suggestion.is_detailed ? "border-green-500 border-2" : "border-gray-300"
                                }`}
                                onClick={() => handleSelectProduct(suggestion.id)}
                            >
                                <div className="flex items-center">
                                    {/* Image Section */}
                                    <div className="flex-shrink-0 w-32 h-32">
                                        <img
                                            src={suggestion.image_url || "placeholder.jpg"}
                                            alt={suggestion.name}
                                            className="w-full h-full object-contain"
                                        />
                                    </div>

                                    {/* Details Section */}
                                    <div className="ml-4 flex-grow text-gray-700">
                                        <p className="text-lg font-medium mb-2">{suggestion.name}</p>
                                        <span
                                            className={`inline-block px-2 py-1 rounded text-sm mb-4 ${
                                                suggestion.is_detailed
                                                    ? "bg-green-100 text-green-700"
                                                    : "bg-yellow-100 text-yellow-700"
                                            }`}
                                        >
                                            {suggestion.is_detailed ? "В системі" : "Потребує скрапінгу"}
                                        </span>
                                        {suggestion.is_detailed && (
                                            <div className="text-sm">
                                                <p>
                                                    <strong>Рейтинг:</strong>{" "}
                                                    {suggestion.average_rating
                                                        ? suggestion.average_rating.toFixed(1)
                                                        : "N/A"}
                                                </p>
                                                <p>
                                                    <strong>Настрої:</strong>
                                                </p>
                                                <ul className="list-disc list-inside">
                                                    <li className="text-green-600">
                                                        Позитивні: {suggestion.sentiments.positive}
                                                    </li>
                                                    <li className="text-yellow-600">
                                                        Нейтральні: {suggestion.sentiments.neutral}
                                                    </li>
                                                    <li className="text-red-600">
                                                        Негативні: {suggestion.sentiments.negative}
                                                    </li>
                                                </ul>
                                            </div>
                                        )}
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

export default HomePage;
