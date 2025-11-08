import { Sidebar } from './components/Sidebar/Sidebar';
import { MainView } from './components/MainView/MainView';
import styles from './App.module.css';

function App() {
  return (
    <div className={styles.app}>
      <Sidebar />
      <MainView />
    </div>
  );
}

export default App;
