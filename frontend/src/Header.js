import { Link } from "react-router-dom";

const Header = () => (
    <nav className="bg-blue-500 p-4 text-white">
        <ul className="flex justify-between">
            <li>
                <Link to="/" className="hover:underline">
                    Головна
                </Link>
            </li>
            <li>
                <Link to="/admin" className="hover:underline">
                    Панель Адміна
                </Link>
            </li>
            <li>
                <Link to="/models" className="hover:underline">
                    Моделі
                </Link>
            </li>
        </ul>
    </nav>
);

export default Header;