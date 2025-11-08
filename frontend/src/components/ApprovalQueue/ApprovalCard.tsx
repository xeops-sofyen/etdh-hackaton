import type { Approval } from '../../types';
import styles from './ApprovalCard.module.css';

interface ApprovalCardProps {
  approval: Approval;
  onApprove: (id: string) => void;
  onDeny: (id: string) => void;
}

export const ApprovalCard = ({ approval, onApprove, onDeny }: ApprovalCardProps) => {
  const getAlertIcon = (type: Approval['type']) => {
    switch (type) {
      case 'deviation':
        return '⚠️';
      case 'anomaly':
        return '🔍';
      case 'high_risk':
        return '⚡';
    }
  };

  const getSeverityClass = (type: Approval['type']) => {
    switch (type) {
      case 'deviation':
        return styles.deviation;
      case 'anomaly':
        return styles.anomaly;
      case 'high_risk':
        return styles.highRisk;
    }
  };

  const getSuggestedAction = (type: Approval['type']) => {
    switch (type) {
      case 'deviation':
        return 'Adjust route to avoid obstacle';
      case 'anomaly':
        return 'Investigate detected activity';
      case 'high_risk':
        return 'Continue with extreme caution';
    }
  };

  return (
    <div className={`${styles.card} ${getSeverityClass(approval.type)}`}>
      <div className={styles.header}>
        <div className={styles.iconContainer}>
          <span className={styles.icon}>{getAlertIcon(approval.type)}</span>
        </div>
        <div className={styles.titleContainer}>
          <span className={styles.severity}>{approval.type.replace('_', ' ')}</span>
          <span className={styles.timestamp}>
            {new Date(approval.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.description}>
          {approval.description}
        </div>

        <div className={styles.suggestedAction}>
          <span className={styles.suggestedLabel}>Suggested Action:</span>
          <span className={styles.suggestedText}>{getSuggestedAction(approval.type)}</span>
        </div>
      </div>

      <div className={styles.actions}>
        <button
          className={`${styles.button} ${styles.denyButton}`}
          onClick={() => onDeny(approval.id)}
        >
          Abort & RTB
        </button>
        <button
          className={`${styles.button} ${styles.approveButton}`}
          onClick={() => onApprove(approval.id)}
        >
          Continue
        </button>
      </div>
    </div>
  );
};
