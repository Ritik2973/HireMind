import sys
import os
from sqlalchemy import select, update

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.connection import SessionLocal
from models.user import User
from models.resume import Resume
from models.interview import InterviewQuestion, Difficulty

QUESTIONS = [
    # Software Engineer - EASY
    {
        "target_job_role": "Software Engineer", "category": "Technical", "difficulty": Difficulty.EASY.value,
        "question_text": "What is the difference between a list and a tuple?",
        "expected_answer": "A list is mutable, meaning its contents can be changed after creation, whereas a tuple is immutable and cannot be altered. Lists use square brackets, and tuples use parentheses.",
        "key_concepts": ["mutable", "immutable", "syntax"],
        "rubric_criteria": ["Mentions list mutability", "Mentions tuple immutability"]
    },
    {
        "target_job_role": "Software Engineer", "category": "Problem Solving", "difficulty": Difficulty.EASY.value,
        "question_text": "How do you approach debugging a piece of code that you did not write?",
        "expected_answer": "I first reproduce the issue consistently. Then I read the surrounding code, use a debugger or logging to trace execution, isolate the failing component, and consult documentation or tests to understand intended behavior.",
        "key_concepts": ["reproduce", "isolate", "logging", "documentation"],
        "rubric_criteria": ["Explains reproduction step", "Mentions isolating the bug", "Mentions using tools like debuggers/logs"]
    },
    {
        "target_job_role": "Software Engineer", "category": "Behavioral", "difficulty": Difficulty.EASY.value,
        "question_text": "Tell me about a time you had to work with a difficult team member.",
        "expected_answer": "I focused on open communication and active listening to understand their perspective. I kept discussions objective and focused on project goals, eventually finding common ground through compromise and empathy.",
        "key_concepts": ["communication", "objective", "empathy", "compromise"],
        "rubric_criteria": ["Focuses on professional resolution", "Mentions empathy or understanding perspective", "Avoids blaming"]
    },
    
    # Software Engineer - MEDIUM
    {
        "target_job_role": "Software Engineer", "category": "Technical", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "How does garbage collection work in Python or Java?",
        "expected_answer": "In Python, it uses reference counting as the primary mechanism, backed by a generational cyclic garbage collector to detect reference cycles. Java uses tracing garbage collectors that identify unreachable objects starting from GC roots.",
        "key_concepts": ["reference counting", "cyclic", "unreachable", "roots"],
        "rubric_criteria": ["Mentions reference counting (Python) or tracing (Java)", "Explains handling of cyclic references or unreachable objects"]
    },
    {
        "target_job_role": "Software Engineer", "category": "Problem Solving", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Explain how you would design a rate limiter for an API.",
        "expected_answer": "I would use a token bucket or leaky bucket algorithm backed by an in-memory store like Redis. I'd track requests per user or IP, decrementing available tokens, and return a 429 status code when limits are exceeded.",
        "key_concepts": ["token bucket", "redis", "429", "in-memory"],
        "rubric_criteria": ["Mentions an algorithm like token bucket", "Mentions fast storage like Redis", "Mentions HTTP 429 response"]
    },
    {
        "target_job_role": "Software Engineer", "category": "Behavioral", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Describe a time when you disagreed with a technical decision made by your manager.",
        "expected_answer": "I presented data and technical trade-offs to support my alternative view in a respectful 1-on-1 meeting. When the manager decided to stick with the original plan due to business constraints, I fully committed to implementing it.",
        "key_concepts": ["data-driven", "respectful", "trade-offs", "commit"],
        "rubric_criteria": ["Used data/evidence to argue", "Maintained professionalism", "Committed to the final decision (disagree and commit)"]
    },
    
    # Software Engineer - HARD
    {
        "target_job_role": "Software Engineer", "category": "Technical", "difficulty": Difficulty.HARD.value,
        "question_text": "Explain race conditions and how to prevent them in a multithreaded application.",
        "expected_answer": "A race condition occurs when multiple threads access shared state concurrently and the outcome depends on execution timing. They are prevented using synchronization primitives like mutexes, locks, semaphores, or by using thread-safe data structures and atomic operations.",
        "key_concepts": ["shared state", "concurrent", "mutexes", "synchronization", "atomic"],
        "rubric_criteria": ["Defines race condition correctly", "Identifies shared state as the cause", "Provides valid prevention mechanisms (locks/mutexes)"]
    },
    {
        "target_job_role": "Software Engineer", "category": "Problem Solving", "difficulty": Difficulty.HARD.value,
        "question_text": "How would you design a scalable URL shortener system like Bitly?",
        "expected_answer": "I would use a relational database for user data and a NoSQL store for URL mappings. I'd generate a unique short code using base62 encoding of an auto-incrementing ID. I'd place a CDN and cache like Redis in front to handle high read loads.",
        "key_concepts": ["base62", "auto-incrementing", "cache", "nosql", "cdn"],
        "rubric_criteria": ["Mentions a valid encoding strategy (base62/hashing)", "Addresses high read throughput (caching/CDN)", "Addresses database selection"]
    },
    {
        "target_job_role": "Software Engineer", "category": "Behavioral", "difficulty": Difficulty.HARD.value,
        "question_text": "Tell me about the most challenging engineering project you've led from inception to delivery.",
        "expected_answer": "I led the migration of a legacy monolith to microservices. The challenge was zero downtime. I planned a strangler fig pattern, coordinated across three teams, established clear API contracts, and rolled it out gradually using feature flags.",
        "key_concepts": ["planning", "coordination", "strangler fig", "gradual rollout", "feature flags"],
        "rubric_criteria": ["Describes a project with significant scope", "Details their specific leadership role", "Explains risk mitigation (gradual rollout/flags)"]
    },

    # Data Scientist - EASY
    {
        "target_job_role": "Data Scientist", "category": "Technical", "difficulty": Difficulty.EASY.value,
        "question_text": "What is the difference between supervised and unsupervised learning?",
        "expected_answer": "Supervised learning uses labeled datasets to train algorithms to classify data or predict outcomes. Unsupervised learning analyzes unlabeled data to discover hidden patterns or groupings, such as clustering.",
        "key_concepts": ["labeled", "unlabeled", "predict", "patterns", "clustering"],
        "rubric_criteria": ["Defines supervised learning via labels", "Defines unsupervised learning via unlabeled data", "Mentions prediction vs pattern discovery"]
    },
    {
        "target_job_role": "Data Scientist", "category": "Problem Solving", "difficulty": Difficulty.EASY.value,
        "question_text": "How do you handle missing values in a dataset?",
        "expected_answer": "I analyze the mechanism of missingness. If random and small, I might drop rows. Otherwise, I impute using mean/median for numericals, mode for categoricals, or use advanced techniques like KNN imputation or predictive modeling.",
        "key_concepts": ["imputation", "drop", "mean", "median", "knn"],
        "rubric_criteria": ["Mentions imputation", "Mentions dropping rows as an option", "Distinguishes between numerical and categorical handling"]
    },
    {
        "target_job_role": "Data Scientist", "category": "Behavioral", "difficulty": Difficulty.EASY.value,
        "question_text": "Tell me about a time you had to explain a complex statistical concept to a non-technical stakeholder.",
        "expected_answer": "I avoided jargon and used a real-world analogy. For instance, explaining random forests by comparing it to asking a diverse council of experts for advice and taking a vote, rather than relying on one person.",
        "key_concepts": ["jargon", "analogy", "business value", "visualizations"],
        "rubric_criteria": ["Mentions avoiding jargon", "Uses analogies or visual aids", "Focuses on audience understanding"]
    },

    # Data Scientist - MEDIUM
    {
        "target_job_role": "Data Scientist", "category": "Technical", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Explain the bias-variance tradeoff in machine learning models.",
        "expected_answer": "Bias is error from erroneous assumptions, causing underfitting. Variance is error from sensitivity to small fluctuations in training data, causing overfitting. The tradeoff involves balancing model complexity to minimize total error.",
        "key_concepts": ["underfitting", "overfitting", "complexity", "total error"],
        "rubric_criteria": ["Defines bias as underfitting", "Defines variance as overfitting", "Explains the balance/tradeoff for total error"]
    },
    {
        "target_job_role": "Data Scientist", "category": "Problem Solving", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "How would you identify and handle severe class imbalance in a classification task?",
        "expected_answer": "I'd check class distribution. To handle it, I'd use metrics like F1-score or PR-AUC instead of accuracy. I'd try resampling techniques like SMOTE for oversampling, or undersampling the majority, and consider class weights in the model.",
        "key_concepts": ["f1-score", "pr-auc", "smote", "resampling", "class weights"],
        "rubric_criteria": ["Rejects simple accuracy as a metric", "Suggests resampling (SMOTE, over/undersampling)", "Mentions algorithmic adjustments like class weights"]
    },
    {
        "target_job_role": "Data Scientist", "category": "Behavioral", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Describe a time when your analysis contradicted a business leader's hypothesis.",
        "expected_answer": "I double-checked my methodology to ensure accuracy. Then I presented the findings objectively, framing it not as proving them wrong, but as discovering a new optimization opportunity, using clear visualizations to tell the data's story.",
        "key_concepts": ["verify", "objective", "visualizations", "opportunity"],
        "rubric_criteria": ["Verified work before presenting", "Maintained objectivity", "Used visualizations/clear communication"]
    },

    # Data Scientist - HARD
    {
        "target_job_role": "Data Scientist", "category": "Technical", "difficulty": Difficulty.HARD.value,
        "question_text": "Explain the mathematical intuition behind backpropagation in neural networks.",
        "expected_answer": "Backpropagation applies the chain rule of calculus to compute the gradient of the loss function with respect to each weight. It passes the error backwards from output to input layers, allowing optimizers like SGD to update weights to minimize loss.",
        "key_concepts": ["chain rule", "gradient", "loss function", "weights", "sgd"],
        "rubric_criteria": ["Mentions chain rule of calculus", "Explains gradients/derivatives", "Explains weight updates minimizing loss"]
    },
    {
        "target_job_role": "Data Scientist", "category": "Problem Solving", "difficulty": Difficulty.HARD.value,
        "question_text": "Design an A/B testing framework for a marketplace platform to measure the impact of a new ranking algorithm.",
        "expected_answer": "I'd define the primary metric (e.g. conversion rate) and guardrail metrics. I'd calculate required sample size for statistical power. I'd randomly assign users to control and treatment, run the test for a full business cycle to avoid weekly seasonality, and evaluate using a t-test.",
        "key_concepts": ["metrics", "sample size", "seasonality", "statistical power", "t-test"],
        "rubric_criteria": ["Defines primary and guardrail metrics", "Addresses statistical power/sample size", "Addresses time/seasonality"]
    },
    {
        "target_job_role": "Data Scientist", "category": "Behavioral", "difficulty": Difficulty.HARD.value,
        "question_text": "Tell me about a time you discovered a critical error in your model after it was already deployed.",
        "expected_answer": "I immediately notified stakeholders and rolled back to the previous version. I performed a root cause analysis, fixed the data pipeline bug, added automated unit tests for data validation, and presented a post-mortem to prevent recurrence.",
        "key_concepts": ["rollback", "notify", "root cause", "post-mortem", "validation"],
        "rubric_criteria": ["Prioritized immediate rollback/mitigation", "Communicated transparently", "Implemented preventative measures"]
    },

    # Machine Learning Engineer - EASY
    {
        "target_job_role": "Machine Learning Engineer", "category": "Technical", "difficulty": Difficulty.EASY.value,
        "question_text": "What are the common evaluation metrics for classification problems?",
        "expected_answer": "Common metrics include accuracy, precision, recall, F1-score, and the Area Under the ROC Curve (AUC-ROC). Precision is used to minimize false positives, while recall minimizes false negatives.",
        "key_concepts": ["accuracy", "precision", "recall", "f1-score", "auc"],
        "rubric_criteria": ["Lists at least 3 valid metrics", "Explains precision vs recall"]
    },
    {
        "target_job_role": "Machine Learning Engineer", "category": "Problem Solving", "difficulty": Difficulty.EASY.value,
        "question_text": "How do you detect overfitting during model training?",
        "expected_answer": "I monitor both training and validation loss during epochs. Overfitting is detected when training loss continues to decrease while validation loss starts to increase or plateau, indicating the model is memorizing training data.",
        "key_concepts": ["validation loss", "training loss", "plateau", "memorizing"],
        "rubric_criteria": ["Mentions comparing training vs validation loss", "Identifies the divergence point"]
    },
    {
        "target_job_role": "Machine Learning Engineer", "category": "Behavioral", "difficulty": Difficulty.EASY.value,
        "question_text": "Tell me about a time you had to collaborate closely with a software engineering team.",
        "expected_answer": "I worked with backend engineers to deploy a model as a microservice. I packaged the model using Docker, defined clear REST API contracts, and optimized the inference code so it met their latency SLAs.",
        "key_concepts": ["docker", "api", "latency", "slas"],
        "rubric_criteria": ["Demonstrates understanding of software engineering concerns (latency/APIs)", "Mentions containerization or deployment tools"]
    },

    # Machine Learning Engineer - MEDIUM
    {
        "target_job_role": "Machine Learning Engineer", "category": "Technical", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Explain how dropout regularization works in deep neural networks.",
        "expected_answer": "Dropout randomly sets a fraction of input units to zero at each update during training time, which helps prevent overfitting by forcing the network to learn redundant representations and not rely on specific neurons.",
        "key_concepts": ["randomly", "zero", "overfitting", "redundant", "training time"],
        "rubric_criteria": ["Explains random neuron deactivation", "States it prevents overfitting", "Mentions it only occurs during training"]
    },
    {
        "target_job_role": "Machine Learning Engineer", "category": "Problem Solving", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "How would you optimize a deep learning model that is taking too long to infer on CPU?",
        "expected_answer": "I would apply model quantization (e.g. FP32 to INT8), use pruning to remove redundant weights, export to an optimized runtime like ONNX or OpenVINO, or use batching if throughput is more important than single-request latency.",
        "key_concepts": ["quantization", "pruning", "onnx", "batching"],
        "rubric_criteria": ["Suggests quantization", "Suggests pruning or optimized runtimes", "Mentions batching trade-offs"]
    },
    {
        "target_job_role": "Machine Learning Engineer", "category": "Behavioral", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Describe a time you had to prioritize speed of delivery over model accuracy.",
        "expected_answer": "We needed a baseline model for a fast-approaching product launch. I deployed a simple, interpretable Logistic Regression model to meet the deadline and establish a pipeline, then incrementally replaced it with a complex ensemble later.",
        "key_concepts": ["baseline", "deadline", "incremental", "simple model"],
        "rubric_criteria": ["Deployed a simple baseline first", "Met the business deadline", "Planned for future iteration"]
    },

    # Machine Learning Engineer - HARD
    {
        "target_job_role": "Machine Learning Engineer", "category": "Technical", "difficulty": Difficulty.HARD.value,
        "question_text": "How do self-attention mechanisms in Transformers differ from recurrent layers in RNNs?",
        "expected_answer": "Self-attention computes representations by comparing each token to all other tokens in the sequence simultaneously, allowing parallelization and capturing long-range dependencies effectively. RNNs process sequences sequentially, suffering from vanishing gradients and blocking parallelization.",
        "key_concepts": ["parallelization", "simultaneously", "long-range", "sequentially", "vanishing gradients"],
        "rubric_criteria": ["Explains self-attention parallelization vs RNN sequential nature", "Mentions long-range dependencies", "Mentions vanishing gradients in RNNs"]
    },
    {
        "target_job_role": "Machine Learning Engineer", "category": "Problem Solving", "difficulty": Difficulty.HARD.value,
        "question_text": "How would you deploy and serve a large LLM in production with high throughput and low latency?",
        "expected_answer": "I would use a framework like vLLM or TensorRT-LLM which implements PagedAttention for efficient KV cache memory management. I'd deploy on multi-GPU instances using tensor parallelism, apply INT8/INT4 quantization, and use dynamic batching.",
        "key_concepts": ["vllm", "pagedattention", "kv cache", "tensor parallelism", "quantization", "batching"],
        "rubric_criteria": ["Mentions advanced serving frameworks (vLLM/TensorRT)", "Mentions KV cache optimization", "Mentions parallelism and quantization"]
    },
    {
        "target_job_role": "Machine Learning Engineer", "category": "Behavioral", "difficulty": Difficulty.HARD.value,
        "question_text": "Tell me about a project where the initial ML approach completely failed and how you pivoted.",
        "expected_answer": "Our deep learning approach for tabular data was failing due to lack of data. I pivoted to an XGBoost model with aggressive feature engineering, which required much less data to converge and ultimately exceeded our accuracy targets.",
        "key_concepts": ["failed", "pivot", "feature engineering", "xgboost", "data constraints"],
        "rubric_criteria": ["Acknowledges failure objectively", "Explains the pivot to a more suitable algorithm", "Addresses the underlying constraint (e.g. data size)"]
    },

    # Backend Developer - EASY
    {
        "target_job_role": "Backend Developer", "category": "Technical", "difficulty": Difficulty.EASY.value,
        "question_text": "What is the difference between SQL and NoSQL databases?",
        "expected_answer": "SQL databases are relational, use structured schemas, and scale vertically, offering strong ACID compliance. NoSQL databases are non-relational, schema-less (document, key-value), and scale horizontally, ideal for unstructured data.",
        "key_concepts": ["relational", "schema", "acid", "horizontal", "vertical"],
        "rubric_criteria": ["Mentions relational vs non-relational", "Mentions schemas", "Mentions scaling differences"]
    },
    {
        "target_job_role": "Backend Developer", "category": "Problem Solving", "difficulty": Difficulty.EASY.value,
        "question_text": "How do you securely store user passwords in a database?",
        "expected_answer": "I never store passwords in plain text. I use a strong, slow cryptographic hashing algorithm like bcrypt or Argon2, which automatically includes a unique salt for each password to protect against rainbow table attacks.",
        "key_concepts": ["plain text", "hashing", "bcrypt", "argon2", "salt"],
        "rubric_criteria": ["Explicitly states never using plain text", "Mentions a modern hashing algorithm (bcrypt/Argon2)", "Explains the use of a salt"]
    },
    {
        "target_job_role": "Backend Developer", "category": "Behavioral", "difficulty": Difficulty.EASY.value,
        "question_text": "Tell me about a time you had to learn a new framework or language on the fly.",
        "expected_answer": "I was assigned to a Go project but only knew Python. I spent the weekend reading the official docs, built a small toy API to understand concurrency with goroutines, and paired with a senior dev to learn team conventions.",
        "key_concepts": ["docs", "toy project", "pairing", "concurrency"],
        "rubric_criteria": ["Shows initiative in learning", "Mentions practical application (building something small)", "Sought help/mentorship"]
    },

    # Backend Developer - MEDIUM
    {
        "target_job_role": "Backend Developer", "category": "Technical", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "How do you implement authentication and authorization using JWT?",
        "expected_answer": "Upon login, the server generates a JWT containing user claims and a signature. The client stores it and sends it in the Authorization header. The server verifies the signature for authentication, and checks claims/roles inside for authorization.",
        "key_concepts": ["claims", "signature", "header", "verify", "roles"],
        "rubric_criteria": ["Explains token generation and signature", "Explains passing via Authorization header", "Distinguishes authentication (verify) and authorization (claims)"]
    },
    {
        "target_job_role": "Backend Developer", "category": "Problem Solving", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "How would you handle a sudden spike in traffic that is overwhelming your database?",
        "expected_answer": "I would implement aggressive read caching using Redis, add read replicas to offload read queries, rate-limit non-critical endpoints, and optimize the slowest queries using indexes or query rewriting.",
        "key_concepts": ["caching", "redis", "read replicas", "rate-limit", "indexes"],
        "rubric_criteria": ["Mentions caching (Redis)", "Mentions read replicas", "Mentions query optimization or rate-limiting"]
    },
    {
        "target_job_role": "Backend Developer", "category": "Behavioral", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Describe a time you had to resolve a critical production outage under pressure.",
        "expected_answer": "I stayed calm, joined the incident bridge, and communicated status. I checked logs and metrics, identified a bad deployment, rolled back immediately to restore service, and then investigated the root cause later to write a post-mortem.",
        "key_concepts": ["calm", "communicate", "rollback", "metrics", "post-mortem"],
        "rubric_criteria": ["Prioritized immediate restoration (rollback)", "Maintained communication", "Followed up with post-mortem"]
    },

    # Backend Developer - HARD
    {
        "target_job_role": "Backend Developer", "category": "Technical", "difficulty": Difficulty.HARD.value,
        "question_text": "Explain the two-phase commit protocol and its drawbacks in distributed systems.",
        "expected_answer": "2PC ensures atomic transactions across multiple nodes via a prepare phase and a commit phase orchestrated by a coordinator. Its drawbacks are that it is a blocking protocol, has a single point of failure at the coordinator, and scales poorly.",
        "key_concepts": ["prepare", "commit", "coordinator", "blocking", "single point of failure"],
        "rubric_criteria": ["Explains prepare and commit phases", "Identifies the coordinator role", "Explains blocking nature/performance issues"]
    },
    {
        "target_job_role": "Backend Developer", "category": "Problem Solving", "difficulty": Difficulty.HARD.value,
        "question_text": "Explain database sharding and partitioning strategies for a high-traffic e-commerce backend.",
        "expected_answer": "I'd use horizontal sharding based on a shard key like user_id or tenant_id to distribute load. For partitioning, I'd use time-based partitioning for order history tables. I must ensure the shard key distributes traffic evenly to avoid hot spots.",
        "key_concepts": ["horizontal", "shard key", "time-based", "distribute", "hot spots"],
        "rubric_criteria": ["Explains horizontal sharding via a shard key", "Explains time-based partitioning for historical data", "Addresses hot spot prevention"]
    },
    {
        "target_job_role": "Backend Developer", "category": "Behavioral", "difficulty": Difficulty.HARD.value,
        "question_text": "Tell me about a time you had to advocate for paying off technical debt over delivering a new feature.",
        "expected_answer": "Our legacy billing system was causing frequent support tickets. I gathered data showing engineering hours wasted on bug fixes versus the time to refactor. I convinced product management to allocate 30% of the sprint to refactoring, significantly reducing incidents.",
        "key_concepts": ["data", "engineering hours", "refactor", "convince", "balance"],
        "rubric_criteria": ["Used data/metrics to argue the case", "Communicated business value to product managers", "Achieved a balanced compromise"]
    },

    # Frontend Developer - EASY
    {
        "target_job_role": "Frontend Developer", "category": "Technical", "difficulty": Difficulty.EASY.value,
        "question_text": "What is the Virtual DOM and how does it improve performance?",
        "expected_answer": "The Virtual DOM is a lightweight JavaScript representation of the actual DOM. React updates the Virtual DOM first, diffs it against the previous version, and calculates the minimal set of real DOM mutations needed, making updates much faster.",
        "key_concepts": ["representation", "diffs", "minimal", "mutations", "faster"],
        "rubric_criteria": ["Defines Virtual DOM as a JS representation", "Explains the diffing process", "Explains batching/minimal real DOM updates"]
    },
    {
        "target_job_role": "Frontend Developer", "category": "Problem Solving", "difficulty": Difficulty.EASY.value,
        "question_text": "How do you ensure a web application is accessible to users with disabilities?",
        "expected_answer": "I use semantic HTML tags, ensure proper ARIA attributes for dynamic content, maintain high color contrast, ensure full keyboard navigability, and test with screen readers like NVDA or VoiceOver.",
        "key_concepts": ["semantic html", "aria", "contrast", "keyboard", "screen readers"],
        "rubric_criteria": ["Mentions semantic HTML and ARIA", "Mentions keyboard navigation", "Mentions screen readers"]
    },
    {
        "target_job_role": "Frontend Developer", "category": "Behavioral", "difficulty": Difficulty.EASY.value,
        "question_text": "Tell me about a time you received negative feedback on a UI component you built.",
        "expected_answer": "A designer pointed out my implementation didn't match the Figma spec for responsive breakpoints. I thanked them, asked for a quick sync to review the exact padding constraints, and updated the CSS to match perfectly.",
        "key_concepts": ["thanked", "sync", "figma", "responsive", "update"],
        "rubric_criteria": ["Accepted feedback without defensiveness", "Collaborated to understand the issue", "Fixed the problem promptly"]
    },

    # Frontend Developer - MEDIUM
    {
        "target_job_role": "Frontend Developer", "category": "Technical", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Explain how React handles state management and side effects with hooks.",
        "expected_answer": "React uses useState for local component state, triggering re-renders on change. Side effects like data fetching or subscriptions are handled by useEffect, which runs after renders and uses a dependency array to control execution frequency.",
        "key_concepts": ["usestate", "re-renders", "useeffect", "dependency array", "data fetching"],
        "rubric_criteria": ["Explains useState and re-rendering", "Explains useEffect for side effects", "Mentions the dependency array"]
    },
    {
        "target_job_role": "Frontend Developer", "category": "Problem Solving", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "How would you track down and fix a memory leak in a Single Page Application?",
        "expected_answer": "I would use Chrome DevTools Memory tab to take heap snapshots and look for detached DOM nodes or growing arrays. Common fixes involve clearing intervals/timeouts, unsubscribing from event listeners, or cleaning up WebSocket connections in unmount hooks.",
        "key_concepts": ["heap snapshots", "detached", "unmount", "event listeners", "intervals"],
        "rubric_criteria": ["Mentions DevTools memory profiling", "Identifies common causes (event listeners/intervals)", "Mentions cleanup during component unmount"]
    },
    {
        "target_job_role": "Frontend Developer", "category": "Behavioral", "difficulty": Difficulty.MEDIUM.value,
        "question_text": "Describe a time you had to bridge the gap between design and engineering.",
        "expected_answer": "A proposed animation was too computationally expensive for lower-end devices. I created a quick prototype of a CSS-only fallback that achieved a similar aesthetic, presented it to the designer, and we agreed to use the performant version.",
        "key_concepts": ["expensive", "prototype", "css-only", "performant", "compromise"],
        "rubric_criteria": ["Identified a technical constraint (performance)", "Proposed a constructive alternative", "Reached a mutual agreement"]
    },

    # Frontend Developer - HARD
    {
        "target_job_role": "Frontend Developer", "category": "Technical", "difficulty": Difficulty.HARD.value,
        "question_text": "How does the browser rendering pipeline work from HTML parsing to painting?",
        "expected_answer": "The browser parses HTML to build the DOM, parses CSS to build the CSSOM, combines them into a Render Tree, calculates Layout (geometry/positions), executes Paint (pixels on layers), and finally Composites the layers onto the screen.",
        "key_concepts": ["dom", "cssom", "render tree", "layout", "paint", "composite"],
        "rubric_criteria": ["Mentions DOM and CSSOM", "Mentions Layout/Reflow", "Mentions Paint and Composite"]
    },
    {
        "target_job_role": "Frontend Developer", "category": "Problem Solving", "difficulty": Difficulty.HARD.value,
        "question_text": "How would you optimize the loading time and bundle size of a massive enterprise SPA?",
        "expected_answer": "I would implement route-level code splitting using dynamic imports. I'd optimize images, use tree-shaking for dependencies, extract vendor chunks, implement server-side rendering or static generation for critical paths, and leverage service workers for caching.",
        "key_concepts": ["code splitting", "tree-shaking", "vendor chunks", "ssr", "caching", "dynamic imports"],
        "rubric_criteria": ["Mentions code splitting/dynamic imports", "Mentions tree-shaking", "Mentions caching or SSR/SSG"]
    },
    {
        "target_job_role": "Frontend Developer", "category": "Behavioral", "difficulty": Difficulty.HARD.value,
        "question_text": "Tell me about a time you mentored a junior developer through a particularly complex frontend challenge.",
        "expected_answer": "A junior was struggling with complex Redux state normalization. Instead of writing it for them, I pair-programmed, asked guiding questions, drew the state tree on a whiteboard, and helped them write pure functions to process the data.",
        "key_concepts": ["pair-programmed", "guiding questions", "whiteboard", "pure functions", "independence"],
        "rubric_criteria": ["Did not just give the answer", "Used pairing or visual aids", "Focused on teaching underlying concepts"]
    },
]

def run_seed():
    db = SessionLocal()
    try:
        # We will iterate through questions. If one exists by (role, text), update it.
        # Else, insert it.
        existing_rows = db.execute(
            select(InterviewQuestion)
        ).scalars().all()
        
        # map (role, text) -> InterviewQuestion object
        existing_map = {(r.target_job_role, r.question_text): r for r in existing_rows}
        
        added_count = 0
        updated_count = 0
        
        for q in QUESTIONS:
            key = (q["target_job_role"], q["question_text"])
            if key in existing_map:
                row = existing_map[key]
                row.expected_answer = q["expected_answer"]
                row.key_concepts = q["key_concepts"]
                row.rubric_criteria = q["rubric_criteria"]
                updated_count += 1
            else:
                new_q = InterviewQuestion(**q)
                db.add(new_q)
                added_count += 1
                
        db.commit()
        print(f"Seed completed. {added_count} new questions added. {updated_count} existing questions updated with M8 metadata.")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
