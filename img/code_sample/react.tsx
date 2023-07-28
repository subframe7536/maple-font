import { useState } from 'react';

export default function Form({ name }) {
  const [isSent, setIsSent] = useState(false);
  const [message, setMessage] = useState(`Hi, ${name}`);
  if (isSent) {
    return <h1>Your message is on its way!</h1>
  }
  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      setIsSent(true);
      postMessage(message);
    }}>
      <textarea
        placeholder="Message"
        value={message}
        onChange={e => setMessage(e.target.value)}
      />
      <button type="submit">Send</button>
    </form>
  );
}
