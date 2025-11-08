import { useState } from 'react';
import { useAppStore } from '../../store/useAppStore';
import { ManualBuilder } from './ManualBuilder';
import { ChatTab } from './ChatTab';
import styles from './PlaybookBuilderModal.module.css';

type BuilderTab = 'manual' | 'chat';

export const PlaybookBuilderModal = () => {
  const { isBuilderOpen, setBuilderOpen } = useAppStore();
  const [activeTab, setActiveTab] = useState<BuilderTab>('manual');

  if (!isBuilderOpen) return null;

  return (
    <div className={styles.overlay} onClick={() => setBuilderOpen(false)}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>Create New Playbook</h2>
          <button
            className={styles.closeButton}
            onClick={() => setBuilderOpen(false)}
          >
            ×
          </button>
        </div>

        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${activeTab === 'manual' ? styles.active : ''}`}
            onClick={() => setActiveTab('manual')}
          >
            Manual Builder
          </button>
          <button
            className={`${styles.tab} ${activeTab === 'chat' ? styles.active : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            Chat with AI
          </button>
        </div>

        <div className={styles.content}>
          {activeTab === 'manual' && <ManualBuilder />}
          {activeTab === 'chat' && <ChatTab />}
        </div>
      </div>
    </div>
  );
};
