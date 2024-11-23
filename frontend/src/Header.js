import { Link } from "react-router-dom";
import {AuthContext} from "./AuthContext";
import {useContext} from "react";

const Header = () => {
    const { user, logout } = useContext(AuthContext);

    return (
        <nav className="bg-blue-500 p-4 text-white">
            <ul className="flex justify-between">
                <li>
                    <Link to="/" className="hover:underline">
                        Головна
                    </Link>
                </li>
                <li>
                    {user?.role === 'admin'
                        &&
                        <Link to="/admin" className="hover:underline">
                            Панель Адміна
                        </Link>
                    }
                </li>
                <li>
                    {user?.role === 'admin'
                        &&
                        <Link to="/models" className="hover:underline">
                            Моделі
                        </Link>
                    }
                </li>
                <li>
                    { user ?
                        <button onClick={logout} className="hover:underline">Вийти з системи {console.log(user)}</button>
                        :
                        <Link to="/login" className="hover:underline">
                            Увійти
                        </Link>
                    }
                </li>
            </ul>
        </nav>
    );
};

export default Header;