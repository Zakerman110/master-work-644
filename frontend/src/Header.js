import { Link } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import { useContext } from "react";

const Header = () => {
    const { user, logout } = useContext(AuthContext);

    return (
        <header className="bg-blue-600 shadow-md">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                {/* Logo */}
                <div className="text-white font-bold text-xl">
                    <Link to="/" className="hover:text-blue-200">
                        Онлайн Агрегатор
                    </Link>
                </div>

                {/* Navigation */}
                <nav className="flex items-center space-x-6">
                    {user?.role === "admin" && (
                        <>
                            <Link to="/admin" className="text-white hover:text-blue-200">
                                Панель Адміна
                            </Link>
                            <Link to="/models" className="text-white hover:text-blue-200">
                                Моделі
                            </Link>
                        </>
                    )}
                    {user ? (
                        <button
                            onClick={logout}
                            className="bg-red-500 px-4 py-2 rounded text-white hover:bg-red-600 transition duration-200"
                        >
                            Вийти
                        </button>
                    ) : (
                        <Link
                            to="/login"
                            className="bg-blue-500 px-4 py-2 rounded text-white hover:bg-blue-400 transition duration-200"
                        >
                            Увійти
                        </Link>
                    )}
                </nav>
            </div>
        </header>
    );
};

export default Header;
