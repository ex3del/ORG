/**
 * Главный компонент приложения.
 * 
 * Этот компонент является корневым для React-приложения и отображает
 * основную структуру интерфейса.
 * 
 * @component
 * @example
 * // Использование в index.js:
 * import App from './App';
 * ReactDOM.render(<App />, document.getElementById('root'));
 * 
 * @returns {JSX.Element} Возвращает JSX-разметку с приветственным заголовком
 */

import React from 'react';

function App() {
  return (
    <div>
      <h1>Welcome to My Pet Project</h1>
    </div>
  );
}

export default App;