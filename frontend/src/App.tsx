import React, { useState, useEffect } from "react";
import type { AuthToken, UserRole } from "./types";
import { Navbar } from "./components/Navbar";
import { Sidebar, type NavTab } from "./components/Sidebar";
import { DashboardPage } from "./pages/DashboardPage";
import { ChatPage } from "./pages/ChatPage";
import { TicketsPage } from "./pages/TicketsPage";
import { TicketDetailPage } from "./pages/TicketDetailPage";
import { ApprovalQueuePage } from "./pages/ApprovalQueuePage";
import { AdminAnalyticsPage } from "./pages/AdminAnalyticsPage";
import { fetchApprovals, switchUser } from "./services/api";

export function App() {
  const [currentUser, setCurrentUser] = useState<AuthToken | null>(() => {
    const saved = localStorage.getItem("support_user");
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState<NavTab>("dashboard");
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const [initialChatPrompt, setInitialChatPrompt] = useState<string>("");
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);

  // Auto-login to demo user if not logged in
  useEffect(() => {
    if (!currentUser) {
      switchUser("usr-nova-cust1")
        .then(setCurrentUser)
        .catch(console.error);
    }
  }, [currentUser]);

  // Periodic poll of approvals count for badge
  useEffect(() => {
    const checkApprovals = () => {
      fetchApprovals("PENDING")
        .then((list) => setPendingApprovalsCount(list.length))
        .catch(() => {});
    };
    checkApprovals();
    const interval = setInterval(checkApprovals, 10000);
    return () => clearInterval(interval);
  }, [currentUser]);

  const handleNavigateToChat = (prompt: string) => {
    setInitialChatPrompt(prompt);
    setActiveTab("chat");
  };

  const handleSelectTicket = (ticketId: string) => {
    setSelectedTicketId(ticketId);
  };

  const handleBackToTickets = () => {
    setSelectedTicketId(null);
  };

  return (
    <div className="app-container">
      <Sidebar
        activeTab={activeTab}
        onTabSelect={(tab) => {
          setActiveTab(tab);
          setSelectedTicketId(null);
        }}
        pendingApprovalsCount={pendingApprovalsCount}
        userRole={currentUser?.role}
      />

      <div className="main-content">
        <Navbar
          currentUser={currentUser}
          onUserChanged={(user) => {
            setCurrentUser(user);
            setSelectedTicketId(null);
          }}
        />

        <main className="flex-1 overflow-y-auto">
          {selectedTicketId ? (
            <TicketDetailPage
              ticketId={selectedTicketId}
              onBack={handleBackToTickets}
            />
          ) : (
            <>
              {activeTab === "dashboard" && (
                <DashboardPage
                  onNavigateToChatWithPrompt={handleNavigateToChat}
                  onSelectTicket={handleSelectTicket}
                />
              )}
              {activeTab === "chat" && (
                <ChatPage initialPrompt={initialChatPrompt} />
              )}
              {activeTab === "tickets" && (
                <TicketsPage onSelectTicket={handleSelectTicket} />
              )}
              {activeTab === "approvals" && <ApprovalQueuePage />}
              {activeTab === "admin" && <AdminAnalyticsPage />}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
