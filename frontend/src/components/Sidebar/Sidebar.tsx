import { useAppStore } from '../../store/useAppStore';
import { PlaybookCard } from './PlaybookCard';
import styles from './Sidebar.module.css';

export const Sidebar = () => {
  const {
    playbooks,
    activeTab,
    setActiveTab,
    setBuilderOpen,
  } = useAppStore();

  const filteredPlaybooks = playbooks.filter((playbook) => {
    if (activeTab === 'active') return playbook.status === 'active';
    if (activeTab === 'planned') return playbook.status === 'planned';
    if (activeTab === 'past')
      return playbook.status === 'completed' || playbook.status === 'failed';
    return false;
  });

  return (
    <div className={styles.sidebar}>
      <div className={styles.header}>
        <h1 className={styles.title}>Drone Mission Control</h1>
        <button
          className={styles.newButton}
          onClick={() => setBuilderOpen(true)}
        >
          + New Playbook
        </button>
      </div>

      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'active' ? styles.active : ''}`}
          onClick={() => setActiveTab('active')}
        >
          Active
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'planned' ? styles.active : ''}`}
          onClick={() => setActiveTab('planned')}
        >
          Planned
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'past' ? styles.active : ''}`}
          onClick={() => setActiveTab('past')}
        >
          Past
        </button>
      </div>

      <div className={styles.playbookList}>
        {filteredPlaybooks.length === 0 ? (
          <div className={styles.emptyState}>
            No {activeTab} missions
          </div>
        ) : (
          filteredPlaybooks.map((playbook) => (
            <PlaybookCard key={playbook.id} playbook={playbook} />
          ))
        )}
      </div>
    </div>
  );
};
