import type { Playbook } from '../../types';
import { useAppStore } from '../../store/useAppStore';
import styles from './PlaybookCard.module.css';

interface PlaybookCardProps {
  playbook: Playbook;
}

export const PlaybookCard = ({ playbook }: PlaybookCardProps) => {
  const { selectedPlaybookId, selectPlaybook } = useAppStore();
  const isSelected = selectedPlaybookId === playbook.id;

  const getMissionIcon = (type: string) => {
    return type === 'surveillance' ? '👁️' : '📦';
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div
      className={`${styles.card} ${isSelected ? styles.selected : ''}`}
      onClick={() => selectPlaybook(playbook.id)}
    >
      <div className={styles.header}>
        <div className={styles.nameRow}>
          <span className={styles.icon}>{getMissionIcon(playbook.missionType)}</span>
          <h3 className={styles.name}>{playbook.name}</h3>
        </div>
        <span className={`${styles.status} ${styles[playbook.status]}`}>
          {playbook.status}
        </span>
      </div>
      <div className={styles.metadata}>
        <span>{playbook.missionType}</span>
        <span>•</span>
        <span>{formatDate(playbook.createdAt)}</span>
      </div>
    </div>
  );
};
