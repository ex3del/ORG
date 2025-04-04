/**
 * Точка входа React-приложения.
 * 
 * Этот код выполняет монтирование корневого компонента App в DOM.
 * Обёртка StrictMode активирует дополнительные проверки React
 * для выявления потенциальных проблем.
 * 
 * @module index
 * @requires react
 * @requires react-dom
 * @requires ./App
 * 
 * @example
 * // При запуске приложения:
 * // 1. React находит элемент с id="root" в public/index.html
 * // 2. Монтирует в него компонент App
 * // 3. Активирует StrictMode-проверки
 */

import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

/**
 * Рендерит приложение в DOM
 * @function
 * @param {JSX.Element} App - Корневой компонент приложения
 * @param {HTMLElement} container - DOM-элемент для монтирования
 */

ReactDOM.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
    document.getElementById('root')
);