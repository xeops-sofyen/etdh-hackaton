import { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { MockLLMService } from '../../services/mockLLM';
import { useAppStore } from '../../store/useAppStore';
import type { Playbook } from '../../types';
import styles from './ChatTab.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const llmService = new MockLLMService();

export const ChatTab = () => {
  const { addPlaybook, setBuilderOpen } = useAppStore();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I can help you create a drone mission. Describe what you'd like the drone to do. For example:\n\n• \"Create a patrol mission around Central Park\"\n• \"Deliver a package from Warehouse A to Drop Zone B\"\n• \"Survey the northern perimeter at 150m altitude\"",
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedPlaybook, setGeneratedPlaybook] = useState<Playbook | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 800));

      const response = await llmService.chat(userMessage);

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.message },
      ]);

      if (response.playbook) {
        setGeneratedPlaybook(response.playbook);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAcceptPlaybook = () => {
    if (generatedPlaybook) {
      addPlaybook(generatedPlaybook);
      setBuilderOpen(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.chatSection}>
        <div className={styles.messages}>
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`${styles.message} ${
                msg.role === 'user' ? styles.userMessage : styles.assistantMessage
              }`}
            >
              <div className={styles.messageContent}>{msg.content}</div>
            </div>
          ))}
          {isLoading && (
            <div className={`${styles.message} ${styles.assistantMessage}`}>
              <div className={styles.messageContent}>
                <div className={styles.typing}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputSection}>
          <textarea
            className={styles.input}
            placeholder="Describe your mission..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            rows={3}
            disabled={isLoading}
          />
          <button
            className={styles.sendButton}
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
          >
            Send
          </button>
        </div>
      </div>

      <div className={styles.previewSection}>
        <div className={styles.previewHeader}>
          <h3 className={styles.previewTitle}>Mission Preview</h3>
          {generatedPlaybook && (
            <button
              className={styles.acceptButton}
              onClick={handleAcceptPlaybook}
            >
              Accept Playbook
            </button>
          )}
        </div>

        {generatedPlaybook ? (
          <div className={styles.preview}>
            <div className={styles.playbookInfo}>
              <div className={styles.infoRow}>
                <span className={styles.label}>Name:</span>
                <span className={styles.value}>{generatedPlaybook.name}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.label}>Type:</span>
                <span className={styles.value}>{generatedPlaybook.missionType}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.label}>Waypoints:</span>
                <span className={styles.value}>
                  {generatedPlaybook.route.features.filter((f) => f.geometry.type === 'Point').length}
                </span>
              </div>
            </div>

            <MapContainer
              center={[49.58, 22.67]}
              zoom={13}
              className={styles.previewMap}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <GeoJSON key={generatedPlaybook.id} data={generatedPlaybook.route} />
            </MapContainer>
          </div>
        ) : (
          <div className={styles.emptyPreview}>
            <p>Describe your mission and I'll show you a preview here</p>
          </div>
        )}
      </div>
    </div>
  );
};
