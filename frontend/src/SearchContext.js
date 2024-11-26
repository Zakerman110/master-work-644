import React, { createContext, useState } from "react";

export const SearchContext = createContext();

export const SearchProvider = ({ children }) => {
    const [searchTerm, setSearchTerm] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("");

    return (
        <SearchContext.Provider
            value={{
                searchTerm,
                setSearchTerm,
                searchResults,
                setSearchResults,
                selectedCategory,
                setSelectedCategory,
            }}
        >
            {children}
        </SearchContext.Provider>
    );
};
