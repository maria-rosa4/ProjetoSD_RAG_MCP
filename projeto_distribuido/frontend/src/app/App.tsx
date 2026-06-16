import { useState, useRef, useEffect } from 'react';
import { ArrowRight, Zap, Circle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: 'Olá! Sou o Assistente de Priorização Inteligente. Estou aqui para ajudá-lo a organizar suas tarefas e prioridades de forma eficiente. Como posso ajudar você hoje?',
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

const handleSend = async () => {
    if (!inputValue.trim()) return;

    // 1. Salva o texto e cria a mensagem do usuário
    const currentQuery = inputValue;
    const newMessage: Message = {
      id: Date.now(), // Usar Date.now() previne bugs de ID duplicado
      text: currentQuery,
      sender: 'user',
      timestamp: new Date(),
    };

    // 2. Coloca a mensagem na tela, limpa o input e ativa a bolinha de "digitando"
    setMessages((prev: Message[]) => [...prev, newMessage]);
    setInputValue('');
    setIsTyping(true);

    // 3. Faz o "transplante" conectando ao seu Orquestrador real
    try {
      const response = await fetch('http://localhost:8000/prioritize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: currentQuery })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao processar a requisição.');
      }

      const data = await response.json();
      
      // 4. Cria a mensagem de resposta da sua IA
      const aiResponse: Message = {
        id: Date.now() + 1,
        text: data.prioritized_response || "Resposta não encontrada.",
        sender: 'ai',
        timestamp: new Date(),
      };
      
      setMessages((prev: Message[]) => [...prev, aiResponse]);

    } catch (error: any) {
      console.error('Erro:', error);
      const errorResponse: Message = {
        id: Date.now() + 1,
        text: 'Erro de conexão com o servidor: ' + error.message,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev: Message[]) => [...prev, errorResponse]);
    } finally {
      setIsTyping(false); // Desliga as bolinhas de "digitando"
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="size-full bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl h-[90vh] flex flex-col bg-slate-900/50 backdrop-blur-xl rounded-2xl shadow-2xl border border-blue-500/20 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600/20 to-cyan-600/20 border-b border-blue-500/30 p-6">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 rounded-full blur-xl opacity-50 animate-pulse"></div>
              <div className="relative bg-gradient-to-br from-blue-500 to-cyan-500 p-3 rounded-full">
                <Zap className="w-6 h-6 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                Assistente de Priorização Inteligente
              </h1>
              <p className="text-blue-300/70 text-sm">Organize suas tarefas com IA</p>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <AnimatePresence>
            {messages.map((message: Message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className={`flex gap-3 ${
                  message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                {/* Avatar */}
                <div
                  className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                    message.sender === 'ai'
                      ? 'bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg shadow-blue-500/50'
                      : 'bg-gradient-to-br from-slate-600 to-slate-700 shadow-lg shadow-slate-500/30'
                  }`}
                >
                  <Circle className={`w-3 h-3 ${message.sender === 'ai' ? 'text-white fill-white' : 'text-white fill-white'}`} />
                </div>

                {/* Message Bubble */}
                <div
                  className={`max-w-[70%] rounded-2xl p-4 ${
                    message.sender === 'ai'
                      ? 'bg-gradient-to-br from-blue-900/40 to-cyan-900/40 border border-blue-500/30 shadow-lg shadow-blue-500/10'
                      : 'bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-600/30'
                  }`}
                >
                  <p className="text-slate-100 leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  <p className="text-xs text-slate-400 mt-2">
                    {message.timestamp.toLocaleTimeString('pt-BR', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3"
            >
              <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg shadow-blue-500/50">
                <Circle className="w-3 h-3 text-white fill-white" />
              </div>
              <div className="bg-gradient-to-br from-blue-900/40 to-cyan-900/40 border border-blue-500/30 rounded-2xl p-4 shadow-lg shadow-blue-500/10">
                <div className="flex gap-1">
                  <motion.div
                    className="w-2 h-2 bg-blue-400 rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-cyan-400 rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-blue-300 rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 bg-gradient-to-r from-slate-900/80 to-blue-950/80 border-t border-blue-500/30 backdrop-blur-sm">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Digite sua mensagem..."
                className="w-full bg-slate-800/50 border border-blue-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
              />
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-cyan-500/5 pointer-events-none"></div>
            </div>
            <button
              onClick={handleSend}
              disabled={!inputValue.trim()}
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:from-slate-700 disabled:to-slate-800 disabled:cursor-not-allowed text-white rounded-xl px-6 py-3 flex items-center gap-2 transition-all shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 disabled:shadow-none"
            >
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>
    </div>
  );
}