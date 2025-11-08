import { Sidebar } from './components/Sidebar/Sidebar';
import { MainView } from './components/MainView/MainView';
import { PlaybookBuilderModal } from './components/PlaybookBuilder/PlaybookBuilderModal';
import styles from './App.module.css';

function App() {
  return (
    <div className={styles.app}>
      <Sidebar />
      <MainView />
      <PlaybookBuilderModal />
    </div>
  );
}

export default App;
