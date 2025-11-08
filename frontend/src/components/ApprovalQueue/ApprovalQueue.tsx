import { useAppStore } from '../../store/useAppStore';
import { ApprovalCard } from './ApprovalCard';
import styles from './ApprovalQueue.module.css';

export const ApprovalQueue = () => {
  const { pendingApprovals, approveAction, denyAction } = useAppStore();

  if (pendingApprovals.length === 0) {
    return null;
  }

  return (
    <div className={styles.queue}>
      <div className={styles.header}>
        <span className={styles.title}>Pending Approvals</span>
        <span className={styles.count}>{pendingApprovals.length}</span>
      </div>

      <div className={styles.cards}>
        {pendingApprovals.map((approval) => (
          <ApprovalCard
            key={approval.id}
            approval={approval}
            onApprove={approveAction}
            onDeny={denyAction}
          />
        ))}
      </div>
    </div>
  );
};
