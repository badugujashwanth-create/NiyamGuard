export default function AssistantTranscript({ messages, liveTranscript }) {
  return (
    <section className="transcript" aria-label="Conversation">
      <div className="section-heading">
        <h3>Conversation</h3>
        <span aria-live="polite">{messages.length} messages</span>
      </div>

      <div className="transcript-list" aria-live="polite">
        {messages.length === 0 && !liveTranscript ? (
          <p className="empty-state">
            Your questions and the assistant's guidance will appear here.
          </p>
        ) : null}

        {messages.map((message) => (
          <article className={`message message-${message.role}`} key={message.id}>
            <span>{message.role === "user" ? "You" : "Assistant"}</span>
            <p>{message.text}</p>
          </article>
        ))}

        {liveTranscript ? (
          <article className="message message-live">
            <span>Voice transcript</span>
            <p>{liveTranscript}</p>
          </article>
        ) : null}
      </div>
    </section>
  );
}
