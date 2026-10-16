import React from "react";

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const s = status.toUpperCase();
  let badgeClass = "badge-indigo";

  if (["DELIVERED", "RESOLVED", "APPROVED", "CAPTURED", "COMPLETED", "SUCCESS"].includes(s)) {
    badgeClass = "badge-green";
  } else if (["PENDING", "PROCESSING", "WAITING_APPROVAL", "AWAITING_APPROVAL"].includes(s)) {
    badgeClass = "badge-amber";
  } else if (["SHIPPED", "IN_PROGRESS", "OPEN"].includes(s)) {
    badgeClass = "badge-cyan";
  } else if (["CANCELLED", "REFUNDED", "FAILED", "REJECTED", "ESCALATED", "ERROR"].includes(s)) {
    badgeClass = "badge-rose";
  }

  return (
    <span className={`badge ${badgeClass}`}>
      <span className="inline-block w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
};
