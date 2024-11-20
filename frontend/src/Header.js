import { Link } from "react-router-dom";

const Header = () => (
    <nav className="bg-blue-500 p-4 text-white">
        <ul className="flex justify-between">
            <li>
                <Link to="/" className="hover:underline">
                    Home
                </Link>
            </li>
            <li>
                <Link to="/admin" className="hover:underline">
                    Admin Panel
                </Link>
            </li>
        </ul>
    </nav>
);

export default Header;