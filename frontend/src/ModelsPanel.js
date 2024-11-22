import React, { useState, useEffect } from "react";
import apiClient from "./axiosConfig";

const ModelsPanel = () => {
    const [models, setModels] = useState([]);
    const [unassociatedReviewsCount, setUnassociatedReviewsCount] = useState(0);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchModels();
    }, []);

    const fetchModels = async () => {
        try {
            const response = await apiClient.get("/api/admin/models/");
            setModels(response.data.models);
            setUnassociatedReviewsCount(response.data.unassociated_reviews_count);
        } catch (err) {
            setError("Error fetching models.");
            console.error(err);
        }
    };

    const handleActivateModel = async (modelId) => {
        try {
            await apiClient.post(`/api/admin/models/${modelId}/activate/`);
            alert("Model activated successfully.");
            fetchModels(); // Refresh the list
        } catch (err) {
            console.error("Error activating model:", err);
            alert("Failed to activate model.");
        }
    };

    const handleTrainModel = async () => {
        try {
            const response = await apiClient.post("/api/admin/models/train/");
            alert("Model training completed successfully.");
            fetchModels(); // Refresh the list of models
        } catch (err) {
            console.error("Error training model:", err);
            alert("Failed to train model.");
        }
    };

    return (
        <div className="p-4">
            <h1 className="text-4xl font-bold text-center mb-8">Панель Адміна - ML Models</h1>

            <button
                onClick={handleTrainModel}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 mb-4"
            >
                Навчити Нову Модель
            </button>

            {error && <p className="text-red-500">{error}</p>}

            <div className="mb-6">
                <p className="text-lg font-bold">
                    Загальна кількість неасоційованих відгуків: {unassociatedReviewsCount}
                </p>
            </div>

            <div className="grid grid-cols-1 gap-4">
                {models.map((model) => (
                    <div
                        key={model.id}
                        className={`p-4 bg-white rounded-lg shadow-md border ${
                            model.is_active ? "border-green-500" : "border-gray-300"
                        }`}
                    >
                        <p><strong>Назва файлу:</strong> {model.file_name}</p>
                        <p><strong>Створено:</strong> {new Date(model.created_at).toLocaleString()}</p>
                        <p><strong>Accuracy:</strong> {model.accuracy.toFixed(2)}</p>
                        <p><strong>Precision:</strong> {model.precision.toFixed(2)}</p>
                        <p><strong>Recall:</strong> {model.recall.toFixed(2)}</p>
                        <p><strong>F1-Score:</strong> {model.f1_score.toFixed(2)}</p>
                        <p><strong>Кількість асоційованих відгуків:</strong> {model.associated_reviews_count}</p>
                        <p><strong>Кількість нових відгуків:</strong> {model.new_reviews_count}</p>
                        <button
                            onClick={() => handleActivateModel(model.id)}
                            className={`px-4 py-2 mt-2 text-white rounded ${
                                model.is_active ? "bg-gray-500 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
                            }`}
                            disabled={model.is_active}
                        >
                            {model.is_active ? "Активна" : "Активувати"}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ModelsPanel;
