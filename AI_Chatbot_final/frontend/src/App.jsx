import React, { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const [darkMode, setDarkMode] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [openSources, setOpenSources] = useState(null);

    const [copiedId, setCopiedId] = useState(null);
    const [feedback, setFeedback] = useState({});

    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);

    // =====================================================
    // LOAD SAVED CHAT
    // =====================================================

    useEffect(() => {
        const savedMessages = localStorage.getItem(
            "campusai_messages"
        );

        const savedTheme = localStorage.getItem(
            "campusai_theme"
        );

        if (savedMessages) {
            setMessages(JSON.parse(savedMessages));
        }

        if (savedTheme === "dark") {
            setDarkMode(true);
        }
    }, []);


    // =====================================================
    // SAVE CHAT
    // =====================================================

    useEffect(() => {
        localStorage.setItem(
            "campusai_messages",
            JSON.stringify(messages)
        );
    }, [messages]);


    // =====================================================
    // SAVE THEME
    // =====================================================

    useEffect(() => {
        localStorage.setItem(
            "campusai_theme",
            darkMode ? "dark" : "light"
        );
    }, [darkMode]);


    // =====================================================
    // AUTO SCROLL
    // =====================================================

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    }, [messages, loading]);


    // =====================================================
    // SEND MESSAGE
    // =====================================================

    const sendMessage = async (customQuestion = null) => {

        const userQuestion = (
            customQuestion !== null
                ? customQuestion
                : question
        ).trim();

        if (!userQuestion || loading) {
            return;
        }

        const userMessage = {
            id: Date.now(),
            type: "user",
            text: userQuestion,
            time: new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit"
            })
        };

        setMessages((prev) => [
            ...prev,
            userMessage
        ]);

        setQuestion("");
        setLoading(true);

        try {

            const response = await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: userQuestion
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "Server error"
                );
            }

            const assistantMessage = {
                id: Date.now() + 1,

                type: "assistant",

                text:
                    data.answer ||
                    "I could not find an answer.",

                sources:
                    data.sources || [],

                time: new Date().toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit"
                })
            };

            setMessages((prev) => [
                ...prev,
                assistantMessage
            ]);

        } catch (error) {

            console.error(error);

            setMessages((prev) => [
                ...prev,
                {
                    id: Date.now() + 1,
                    type: "assistant",
                    text:
                        "Unable to connect to the backend. Please try again.",
                    sources: [],
                    error: true,
                    time: new Date().toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit"
                    })
                }
            ]);

        } finally {
            setLoading(false);
        }
    };


    // =====================================================
    // NEW CONVERSATION
    // =====================================================

    const newConversation = () => {

        setMessages([]);
        setQuestion("");
        setOpenSources(null);

        localStorage.removeItem(
            "campusai_messages"
        );
    };


    // =====================================================
    // COPY ANSWER
    // =====================================================

    const copyAnswer = async (text, id) => {

        try {

            await navigator.clipboard.writeText(text);

            setCopiedId(id);

            setTimeout(() => {
                setCopiedId(null);
            }, 1500);

        } catch (error) {
            console.error(error);
        }
    };


    // =====================================================
    // READ ALOUD
    // =====================================================

    const readAnswer = (text) => {

        if ("speechSynthesis" in window) {

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(text);

            speech.rate = 0.95;
            speech.pitch = 1;

            window.speechSynthesis.speak(
                speech
            );
        }
    };


    // =====================================================
    // FEEDBACK
    // =====================================================

    const giveFeedback = (id, value) => {

        setFeedback((prev) => ({
            ...prev,
            [id]: value
        }));
    };


    // =====================================================
    // REGENERATE
    // =====================================================

    const regenerate = (messageId) => {

        const index = messages.findIndex(
            (message) =>
                message.id === messageId
        );

        if (index === -1) return;

        const previousUserMessage =
            messages[index - 1];

        if (
            previousUserMessage &&
            previousUserMessage.type === "user"
        ) {

            setMessages((prev) =>
                prev.slice(0, index)
            );

            sendMessage(
                previousUserMessage.text
            );
        }
    };


    // =====================================================
    // VOICE INPUT
    // =====================================================

    const startVoiceInput = () => {

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (!SpeechRecognition) {

            alert(
                "Voice input is not supported in this browser. Try Google Chrome."
            );

            return;
        }

        const recognition =
            new SpeechRecognition();

        recognition.lang = "en-IN";

        recognition.continuous = false;

        recognition.interimResults = false;

        recognition.onresult = (event) => {

            const transcript =
                event.results[0][0].transcript;

            setQuestion(
                (prev) =>
                    prev
                        ? prev + " " + transcript
                        : transcript
            );
        };

        recognition.start();
    };


    // =====================================================
    // QUICK QUESTIONS
    // =====================================================

    const quickQuestions = [
        {
            icon: "💰",
            title: "Fee Structure",
            description: "Check course fees",
            question:
                "What is the fee structure?"
        },

        {
            icon: "📅",
            title: "Academic Calendar",
            description: "Important academic dates",
            question:
                "What is the academic calendar?"
        },

        {
            icon: "👤",
            title: "University Officials",
            description: "Find university officials",
            question:
                "Who is the Vice Chancellor?"
        },

        {
            icon: "📢",
            title: "Latest Notices",
            description: "Check university notices",
            question:
                "What are the latest notices?"
        },

        {
            icon: "📊",
            title: "Student Analytics",
            description: "Student information",
            question:
                "How many students are registered?"
        },

        {
            icon: "📋",
            title: "Student Guidelines",
            description: "Rules and regulations",
            question:
                "What are the student guidelines?"
        }
    ];


    // =====================================================
    // ENTER KEY
    // =====================================================

    const handleKeyDown = (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    };


    // =====================================================
    // AUTO RESIZE TEXTAREA
    // =====================================================

    const handleInput = (event) => {

        setQuestion(event.target.value);

        const textarea =
            textareaRef.current;

        if (textarea) {

            textarea.style.height = "auto";

            textarea.style.height =
                Math.min(
                    textarea.scrollHeight,
                    130
                ) + "px";
        }
    };


    return (

        <div
            className={
                darkMode
                    ? "app-container dark"
                    : "app-container"
            }
        >

            {/* =================================================
                SIDEBAR
            ================================================= */}

            {sidebarOpen && (

                <aside className="sidebar">

                    <div className="sidebar-top">

                        {/* BRAND */}

                        <div className="brand">

                            <div className="brand-logo">
                                ✦
                            </div>

                            <div>

                                <div className="brand-title">
                                    ITM Nova
                                </div>

                                <div className="brand-subtitle">
                                    Student Support
                                </div>

                            </div>

                        </div>


                        {/* NEW CHAT */}

                        <button
                            className="new-chat-btn"
                            onClick={
                                newConversation
                            }
                        >

                            <span>＋</span>

                            New Conversation

                        </button>


                        {/* SEARCH */}

                        <div className="chat-search">

                            <span>⌕</span>

                            <input
                                placeholder="Search conversations..."
                            />

                        </div>


                        {/* QUICK ACCESS */}

                        <div className="sidebar-section">

                            <div className="section-title">
                                QUICK ACCESS
                            </div>

                            {quickQuestions
                                .slice(0, 4)
                                .map(
                                    (
                                        item,
                                        index
                                    ) => (

                                        <button
                                            key={index}
                                            className="sidebar-link"
                                            onClick={() =>
                                                sendMessage(
                                                    item.question
                                                )
                                            }
                                        >

                                            <span>
                                                {
                                                    item.icon
                                                }
                                            </span>

                                            <div>

                                                <strong>
                                                    {
                                                        item.title
                                                    }
                                                </strong>

                                                <small>
                                                    {
                                                        item.description
                                                    }
                                                </small>

                                            </div>

                                        </button>

                                    )
                                )}

                        </div>

                    </div>


                    {/* SIDEBAR BOTTOM */}

                    <div className="sidebar-bottom">

                        <div className="ai-status-card">

                            <div className="ai-status-icon">
                                ✨
                            </div>

                            <div>

                                <strong>
                                    ITM Nova
                                </strong>

                                <span>
                                    AI Assistant
                                </span>

                            </div>

                            <div className="status-dot"></div>

                        </div>

                    </div>

                </aside>

            )}


            {/* =================================================
                MAIN CONTENT
            ================================================= */}

            <main className="main-content">


                {/* HEADER */}

                <header className="top-header">

                    <div className="header-left">

                        <button
                            className="menu-button"
                            onClick={() =>
                                setSidebarOpen(
                                    !sidebarOpen
                                )
                            }
                        >
                            ☰
                        </button>

                        <div>

                            <h1>
                                Student Support Assistant
                            </h1>

                            <p>
                                Your intelligent university companion
                            </p>

                        </div>

                    </div>


                    <div className="header-actions">

                       

                        <button
                            className="theme-button"
                            onClick={() =>
                                setDarkMode(
                                    !darkMode
                                )
                            }
                        >
                            {darkMode
                                ? "☀️"
                                : "🌙"}
                        </button>

                    </div>

                </header>


                {/* CHAT */}

                <div className="chat-area">

                    {messages.length === 0 ? (

                        /* =================================================
                           WELCOME
                        ================================================= */

                        <div className="welcome-container">

                            <div className="welcome-orb">

                                <div className="orb-ring ring-one"></div>

                                <div className="orb-ring ring-two"></div>

                                <div className="robot-face">

                                    <div className="robot-eye"></div>

                                    <div className="robot-eye"></div>

                                    <div className="robot-mouth"></div>

                                </div>

                            </div>


                            <div className="welcome-badge">
                                ✨ AI POWERED
                            </div>


                            <h2>
                                Hello, I'm{" "}
                                <span>
                                    ITM Nova
                                </span>
                            </h2>

                            <p className="welcome-text">

                                Your AI-powered student
                                support assistant. Ask me
                                about university information,
                                fees, academics, notices,
                                officials and more.

                            </p>


                            {/* QUICK CARDS */}

                            <div className="suggestions">

                                {quickQuestions.map(
                                    (
                                        item,
                                        index
                                    ) => (

                                        <button
                                            className="suggestion-card"
                                            key={index}
                                            onClick={() =>
                                                sendMessage(
                                                    item.question
                                                )
                                            }
                                        >

                                            <div className="suggestion-icon">
                                                {
                                                    item.icon
                                                }
                                            </div>

                                            <div>

                                                <strong>
                                                    {
                                                        item.title
                                                    }
                                                </strong>

                                                <small>
                                                    {
                                                        item.description
                                                    }
                                                </small>

                                            </div>

                                            <span className="card-arrow">
                                                →
                                            </span>

                                        </button>

                                    )
                                )}

                            </div>

                        </div>

                    ) : (

                        /* =================================================
                           MESSAGES
                        ================================================= */

                        <div className="messages">

                            {messages.map(
                                (message) => (

                                    <div
                                        key={
                                            message.id
                                        }
                                        className={
                                            message.type ===
                                            "user"
                                                ? "message-row user-row"
                                                : "message-row assistant-row"
                                        }
                                    >

                                        {/* AVATAR */}

                                      


                                        {/* CONTENT */}

                                        <div className="message-content">

                                            <div className="message-header">

                                                <strong>
                                                    {message.type ===
                                                    "user"
                                                        ? "You"
                                                        : "ITM Nova"}
                                                </strong>

                                                <span>
                                                    {
                                                        message.time
                                                    }
                                                </span>

                                            </div>


                                            <div
                                                className={
                                                    message.type ===
                                                    "user"
                                                        ? "message-bubble user-bubble"
                                                        : "message-bubble assistant-bubble"
                                                }
                                            >

                                                {message.text}

                                            </div>


                                            {/* AI TOOLS */}

                                            {message.type ===
                                                "assistant" &&
                                                !message.error && (

                                                    <div className="message-tools">

                                                        <button
                                                            onClick={() =>
                                                                copyAnswer(
                                                                    message.text,
                                                                    message.id
                                                                )
                                                            }
                                                        >
                                                            {copiedId ===
                                                            message.id
                                                                ? "✓ Copied"
                                                                : "📋 Copy"}
                                                        </button>

                                                        <button
                                                            onClick={() =>
                                                                readAnswer(
                                                                    message.text
                                                                )
                                                            }
                                                        >
                                                            🔊 Listen
                                                        </button>

                                                        

                                                        <span className="tool-divider">
                                                        </span>

                                                       

                                                       

                                                    </div>

                                                )}


                                            {/* SOURCES */}

                                            {message.type ===
                                                "assistant" &&
                                                message.sources &&
                                                message.sources.length >
                                                    0 && (

                                                    <div className="sources-box">

                                                        <button
                                                            className="sources-toggle"
                                                            onClick={() =>
                                                                setOpenSources(
                                                                    openSources ===
                                                                    message.id
                                                                        ? null
                                                                        : message.id
                                                                )
                                                            }
                                                        >

                                                            <span>
                                                                📚
                                                                Verified Sources
                                                            </span>

                                                            <span className="source-count">
                                                                {
                                                                    message.sources.length
                                                                }
                                                            </span>

                                                            <span>
                                                                {openSources ===
                                                                message.id
                                                                    ? "▲"
                                                                    : "▼"}
                                                            </span>

                                                        </button>


                                                        {openSources ===
                                                            message.id && (

                                                            <div className="sources-list">

                                                                {message.sources.map(
                                                                    (
                                                                        source,
                                                                        index
                                                                    ) => (

                                                                        <div
                                                                            className="source-item"
                                                                            key={
                                                                                index
                                                                            }
                                                                        >

                                                                            <span>
                                                                                📄
                                                                            </span>

                                                                            <div>

                                                                                <strong>
                                                                                    {
                                                                                        source.source ||
                                                                                        "University Document"
                                                                                    }
                                                                                </strong>

                                                                                {source.page !==
                                                                                    undefined &&
                                                                                    source.page !==
                                                                                        null && (
                                                                                        <small>
                                                                                            Page{" "}
                                                                                            {
                                                                                                source.page
                                                                                            }
                                                                                        </small>
                                                                                    )}

                                                                            </div>

                                                                        </div>

                                                                    )
                                                                )}

                                                            </div>

                                                        )}

                                                    </div>

                                                )}

                                        </div>

                                    </div>

                                )
                            )}


                            {/* LOADING */}

                            {loading && (

                                <div className="message-row assistant-row">

                                    <div className="avatar assistant-avatar">
                                        ✦
                                    </div>

                                    <div className="message-content">

                                        <div className="message-header">

                                            <strong>
                                                CampusAI
                                            </strong>

                                            <span>
                                                Thinking...
                                            </span>

                                        </div>

                                        <div className="typing-bubble">

                                            <span></span>
                                            <span></span>
                                            <span></span>

                                        </div>

                                    </div>

                                </div>

                            )}

                            <div
                                ref={
                                    messagesEndRef
                                }
                            />

                        </div>

                    )}

                </div>


                {/* =================================================
                   INPUT
                ================================================= */}

                <div className="input-area">

                    <div className="input-wrapper">

                        <button
                            className="input-icon"
                            onClick={
                                startVoiceInput
                            }
                            title="Voice input"
                        >
                            🎤
                        </button>


                        <textarea
                            ref={
                                textareaRef
                            }
                            value={
                                question
                            }
                            onChange={
                                handleInput
                            }
                            onKeyDown={
                                handleKeyDown
                            }
                            placeholder="Ask ITM Nova anything..."
                            rows="1"
                            disabled={
                                loading
                            }
                        />


                        <button
                            className="send-button"
                            onClick={() =>
                                sendMessage()
                            }
                            disabled={
                                loading ||
                                !question.trim()
                            }
                        >
                            ➤
                        </button>

                    </div>

                    <div className="input-footer">

                        <span>
                            ✦ CampusAI can answer questions
                            using university knowledge
                        </span>

                        <span>
                            Enter ↵ to send
                        </span>

                    </div>

                </div>

            </main>

        </div>
    );
}

export default App;