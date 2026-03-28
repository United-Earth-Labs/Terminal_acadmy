"""Create React from Zero to Hero course — Module 1: React Foundations."""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from courses.models import Category, Course, Module, Lesson, Quiz, QuizQuestion, QuizAnswer
from labs.models import Lab

print('Creating React course (Module 1)...')

# ── Category ──────────────────────────────────────────────────────────
webdev_cat, _ = Category.objects.get_or_create(
    slug='web-development',
    defaults={
        'name': 'Web Development',
        'description': 'Frontend and fullstack web development courses',
        'icon': '🌐',
        'order': 2,
    }
)
print('✓ Category ready')

# ── Course ────────────────────────────────────────────────────────────
react_course, _ = Course.objects.get_or_create(
    slug='react-zero-to-hero',
    defaults={
        'title': 'React from Zero to Hero',
        'short_description': 'Learn React from scratch — no prior experience needed',
        'description': (
            'A beginner-friendly journey through React. Every concept starts with a '
            'real-world analogy, followed by clear explanations, code examples, and '
            'interactive demos you can play with. By the end you will be comfortable '
            'building modern React apps on your own.'
        ),
        'category': webdev_cat,
        'level': 'beginner',
        'status': 'published',
        'is_featured': True,
        'xp_reward': 500,
        'estimated_duration': 480,
    }
)
print('✓ Course ready')

# ── Module 1: React Foundations ───────────────────────────────────────
mod1, _ = Module.objects.get_or_create(
    course=react_course,
    order=1,
    defaults={
        'title': 'React Foundations',
        'description': 'Understand what React is, write your first component, learn JSX, and pass data with props.',
    }
)
print('✓ Module 1 ready')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 1 — What is React & Why Use It
# ═══════════════════════════════════════════════════════════════════════
L1_CONTENT = """## 🍕 Real-World Analogy

Imagine you're building a house with LEGO bricks. Each brick is a small, reusable piece. You can snap them together to create anything — a wall, a window, a door. If one brick breaks, you swap just that one brick instead of rebuilding the entire house.

**React works the same way.** Your web page is built from small, reusable "components" (bricks). Change one component and only that part of the page updates — the rest stays untouched.

---

## 🧠 What is React?

React is a **JavaScript library** created by Facebook (now Meta) for building user interfaces. It lets you break your UI into small, independent pieces called **components**.

### Why developers love React:
- **Component-based** — build small pieces, combine them into big apps
- **Declarative** — you describe WHAT you want, React figures out HOW to update the screen
- **Fast** — React only re-renders parts that changed (Virtual DOM)
- **Huge ecosystem** — millions of developers, tons of libraries, massive job market

### Traditional HTML vs React

**Traditional approach:** You write one giant HTML file. Need to change something? You manually find and update every affected part.

**React approach:** Each piece of your UI is a component. Change the data, React automatically updates only what's needed.

---

## 💻 Code Example

Here's what a tiny React app looks like:

```jsx
// This is a React component — just a JavaScript function!
function WelcomeMessage() {
  return <h1>Hello, future React developer! 🚀</h1>;
}

// This renders your component to the screen
ReactDOM.render(<WelcomeMessage />, document.getElementById('root'));
```

That `<h1>Hello...</h1>` inside JavaScript? That's called **JSX** — we'll learn about it in Lesson 3!

---

## 🎮 Try It Yourself

Think of a website you use daily (Instagram, YouTube, Twitter). Try to identify the "components" — the search bar, the post card, the navbar, the like button. Each of those would be a separate React component!

---

## 🔑 Key Takeaways

- React is a JavaScript library for building UIs from reusable components
- It uses a Virtual DOM to efficiently update only what changes
- Components are like LEGO bricks — small, reusable, and composable
- React is declarative: you describe the result, not the steps to get there
"""

les1, _ = Lesson.objects.get_or_create(
    module=mod1, slug='what-is-react',
    defaults={
        'title': 'What is React & Why Use It',
        'content': L1_CONTENT,
        'content_type': 'text',
        'order': 1,
        'xp_reward': 15,
        'estimated_duration': 10,
    }
)

q1, _ = Quiz.objects.get_or_create(lesson=les1, defaults={
    'title': 'What is React? — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq1a, _ = QuizQuestion.objects.get_or_create(quiz=q1, order=1, defaults={
    'question_text': 'What is React primarily used for?',
    'question_type': 'single',
    'explanation': 'React is a JavaScript library specifically designed for building user interfaces.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq1a, order=1, defaults={'answer_text': 'Building user interfaces', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq1a, order=2, defaults={'answer_text': 'Managing databases', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq1a, order=3, defaults={'answer_text': 'Writing server-side APIs', 'is_correct': False})

qq1b, _ = QuizQuestion.objects.get_or_create(quiz=q1, order=2, defaults={
    'question_text': 'What technique does React use to efficiently update the screen?',
    'question_type': 'single',
    'explanation': 'React uses a Virtual DOM to compare changes and update only the parts that actually changed.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq1b, order=1, defaults={'answer_text': 'It reloads the entire page', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq1b, order=2, defaults={'answer_text': 'Virtual DOM', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq1b, order=3, defaults={'answer_text': 'Server-side rendering only', 'is_correct': False})

qq1c, _ = QuizQuestion.objects.get_or_create(quiz=q1, order=3, defaults={
    'question_text': 'In our LEGO analogy, what does a single LEGO brick represent?',
    'question_type': 'single',
    'explanation': 'Each LEGO brick represents a React component — a small, reusable piece of UI.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq1c, order=1, defaults={'answer_text': 'The entire web page', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq1c, order=2, defaults={'answer_text': 'A CSS stylesheet', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq1c, order=3, defaults={'answer_text': 'A React component', 'is_correct': True})

print('  ✓ Lesson 1 + quiz')

l1_lab, _ = Lab.objects.get_or_create(
    lesson=les1,
    defaults={
        'title': 'Hello React!',
        'description': 'Write your first React component to welcome users.',
        'instructions': '1. Create a function called WelcomeMessage.\n2. Return an <h1> tag containing exactly "Welcome to React!".\n3. Render it to the root element using ReactDOM.createRoot.',
        'difficulty': 'easy',
        'xp_reward': 20,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'function WelcomeMessage', 'description': 'Create a WelcomeMessage component'},
            {'type': 'frontend_render', 'contains': 'Welcome to React!', 'description': 'Render the correct welcome text'},
        ],
        'hints': [
            'Make sure you spell the function name exactly as `WelcomeMessage` with a capital W.',
            'Remember to return some JSX like `return <h1>...</h1>`.',
            'You can render it by using `const root = ReactDOM.createRoot(document.getElementById("root")); root.render(<WelcomeMessage />);`'
        ],
        'flags': ['react_l1_flag'],
    }
)
print('  ✓ Lesson 1 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 2 — Your First Component
# ═══════════════════════════════════════════════════════════════════════
L2_CONTENT = """## 🍳 Real-World Analogy

Think of a **recipe card** in a kitchen. Each card describes exactly how to make one dish. You can use that same card over and over whenever someone orders that dish.

A React **component** is your recipe card — it describes exactly what should appear on screen. Use it once, use it ten times — same recipe, same result.

---

## 🧠 What is a Component?

A component is just a **JavaScript function that returns HTML-like code** (JSX). That's it!

### Rules for components:
1. The function name must start with a **Capital letter** (React rule!)
2. It must **return** some JSX (the HTML-like stuff)
3. You use it like an HTML tag: `<MyComponent />`

---

## 💻 Code Example

```jsx
// Step 1: Define your component (the "recipe card")
function Greeting() {
  return (
    <div>
      <h1>Hey there! 👋</h1>
      <p>Welcome to your first React component!</p>
    </div>
  );
}

// Step 2: Use it! Just like an HTML tag
function App() {
  return (
    <div>
      <Greeting />
      <Greeting />
      <Greeting />
    </div>
  );
}
```

See how we used `<Greeting />` three times? That's the power of components — **write once, use everywhere!**

### Breaking a page into components:

```jsx
function Navbar() {
  return <nav>Terminal Academy</nav>;
}

function HeroSection() {
  return <h1>Learn React Today!</h1>;
}

function Footer() {
  return <footer>© 2026 Terminal Academy</footer>;
}

// Put them all together
function App() {
  return (
    <div>
      <Navbar />
      <HeroSection />
      <Footer />
    </div>
  );
}
```

---

## 🎮 Try It Yourself

Look at this very page you're reading right now. The navbar at the top, the lesson content area, the sidebar — each could be its own component. Try sketching out component names for a simple to-do app: maybe `TodoItem`, `TodoList`, `AddTodoButton`.

---

## 🔑 Key Takeaways

- A component is a function that returns JSX
- Component names MUST start with a capital letter
- You reuse components like HTML tags: `<MyComponent />`
- Break your UI into small, focused components
"""

les2, _ = Lesson.objects.get_or_create(
    module=mod1, slug='your-first-component',
    defaults={
        'title': 'Your First Component',
        'content': L2_CONTENT,
        'content_type': 'text',
        'order': 2,
        'xp_reward': 15,
        'estimated_duration': 12,
    }
)

q2, _ = Quiz.objects.get_or_create(lesson=les2, defaults={
    'title': 'Your First Component — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq2a, _ = QuizQuestion.objects.get_or_create(quiz=q2, order=1, defaults={
    'question_text': 'What must a React component function always do?',
    'question_type': 'single',
    'explanation': 'Every React component must return JSX that describes what should be rendered.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq2a, order=1, defaults={'answer_text': 'Return JSX', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq2a, order=2, defaults={'answer_text': 'Call an API', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq2a, order=3, defaults={'answer_text': 'Use a class keyword', 'is_correct': False})

qq2b, _ = QuizQuestion.objects.get_or_create(quiz=q2, order=2, defaults={
    'question_text': 'Why must component names start with a capital letter?',
    'question_type': 'single',
    'explanation': 'React uses the capital letter to distinguish your custom components from regular HTML tags like <div> or <p>.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq2b, order=1, defaults={'answer_text': 'It looks nicer', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq2b, order=2, defaults={'answer_text': 'React distinguishes components from HTML tags', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq2b, order=3, defaults={'answer_text': 'JavaScript requires it', 'is_correct': False})

qq2c, _ = QuizQuestion.objects.get_or_create(quiz=q2, order=3, defaults={
    'question_text': 'How do you reuse a component called ProfileCard?',
    'question_type': 'single',
    'explanation': 'You use a component like an HTML tag with angle brackets and a self-closing slash.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq2c, order=1, defaults={'answer_text': 'ProfileCard()', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq2c, order=2, defaults={'answer_text': '<ProfileCard />', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq2c, order=3, defaults={'answer_text': 'import ProfileCard', 'is_correct': False})

print('  ✓ Lesson 2 + quiz')

l2_lab, _ = Lab.objects.get_or_create(
    lesson=les2,
    defaults={
        'title': 'Composing Components',
        'description': 'Break a page into smaller, reusable components.',
        'instructions': 'Create a `SiteHeader` component and a `SiteFooter` component. Use both of them inside an `App` component.',
        'difficulty': 'medium',
        'xp_reward': 25,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'function SiteHeader', 'description': 'Create SiteHeader component'},
            {'type': 'frontend_code', 'contains': 'function SiteFooter', 'description': 'Create SiteFooter component'},
            {'type': 'frontend_code', 'contains': '<SiteHeader />', 'description': 'Use SiteHeader inside App'},
        ],
        'hints': [
            'Start by creating three separate functions: SiteHeader, SiteFooter, and App.',
            'In App, you should return a `<div>` that contains both `<SiteHeader />` and `<SiteFooter />`.',
            'Don\'t forget that all component functions must start with a capital letter!'
        ],
        'flags': ['react_l2_flag'],
    }
)
print('  ✓ Lesson 2 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 3 — JSX Basics
# ═══════════════════════════════════════════════════════════════════════
L3_CONTENT = """## 🗣️ Real-World Analogy

Imagine you speak two languages — English and Spanish. Sometimes it's easier to mix both in the same sentence: "Let's go to the tienda to buy leche." You combine them because it's more natural.

**JSX** is exactly that — it lets you write HTML inside JavaScript. It combines the best of both worlds so you can describe your UI naturally.

---

## 🧠 What is JSX?

JSX stands for **JavaScript XML**. It looks like HTML but lives inside your JavaScript code. Under the hood, React converts it into regular JavaScript.

### JSX Rules:
1. **Return one parent element** — wrap everything in a single `<div>` or `<>...</>`
2. **Use `className`** instead of `class` (because `class` is reserved in JS)
3. **Use curly braces `{}`** to embed JavaScript expressions
4. **Close all tags** — even self-closing ones like `<img />`, `<br />`

---

## 💻 Code Example

```jsx
function UserProfile() {
  const name = "Sarah";
  const age = 25;
  const isOnline = true;

  return (
    <div className="profile-card">
      {/* This is a JSX comment */}
      <h2>Hello, {name}!</h2>
      <p>Age: {age}</p>
      <p>Status: {isOnline ? "🟢 Online" : "🔴 Offline"}</p>
      <p>Next birthday: age {age + 1}</p>
      <img src="avatar.png" alt="User avatar" />
    </div>
  );
}
```

Notice the curly braces `{}` — that's where JavaScript lives inside JSX! You can put any JavaScript **expression** inside: variables, math, ternary operators, function calls.

### What you CAN'T put in curly braces:
```jsx
// ❌ No if/else statements
<p>{if (true) "yes"}</p>

// ✅ Use ternary instead
<p>{true ? "yes" : "no"}</p>

// ❌ No for loops
<p>{for (let i=0; i<3; i++) ...}</p>

// ✅ Use .map() instead (we'll learn this later!)
```

---

## 🎮 Try It Yourself

Try to mentally "translate" this HTML into JSX. What needs to change?

```html
<div class="card">
  <label for="name">Name</label>
  <img src="pic.jpg">
</div>
```

Answer: `class` → `className`, `for` → `htmlFor`, `<img>` → `<img />`

---

## 🔑 Key Takeaways

- JSX lets you write HTML-like code inside JavaScript
- Use `className` instead of `class`
- Use curly braces `{}` to embed JavaScript expressions
- Every JSX must return ONE parent element
- Always close your tags: `<img />`, `<input />`, `<br />`
"""

les3, _ = Lesson.objects.get_or_create(
    module=mod1, slug='jsx-basics',
    defaults={
        'title': 'JSX Basics',
        'content': L3_CONTENT,
        'content_type': 'text',
        'order': 3,
        'xp_reward': 15,
        'estimated_duration': 12,
    }
)

q3, _ = Quiz.objects.get_or_create(lesson=les3, defaults={
    'title': 'JSX Basics — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq3a, _ = QuizQuestion.objects.get_or_create(quiz=q3, order=1, defaults={
    'question_text': 'In JSX, how do you apply a CSS class to an element?',
    'question_type': 'single',
    'explanation': 'In JSX you use className because class is a reserved keyword in JavaScript.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq3a, order=1, defaults={'answer_text': 'class="name"', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq3a, order=2, defaults={'answer_text': 'className="name"', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq3a, order=3, defaults={'answer_text': 'cssClass="name"', 'is_correct': False})

qq3b, _ = QuizQuestion.objects.get_or_create(quiz=q3, order=2, defaults={
    'question_text': 'How do you embed a JavaScript variable called "score" inside JSX?',
    'question_type': 'single',
    'explanation': 'Curly braces {} are used in JSX to embed JavaScript expressions.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq3b, order=1, defaults={'answer_text': '{{score}}', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq3b, order=2, defaults={'answer_text': '${score}', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq3b, order=3, defaults={'answer_text': '{score}', 'is_correct': True})

qq3c, _ = QuizQuestion.objects.get_or_create(quiz=q3, order=3, defaults={
    'question_text': 'What does JSX stand for?',
    'question_type': 'single',
    'explanation': 'JSX stands for JavaScript XML — a syntax extension that looks like HTML.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq3c, order=1, defaults={'answer_text': 'JavaScript XML', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq3c, order=2, defaults={'answer_text': 'Java Syntax Extension', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq3c, order=3, defaults={'answer_text': 'JSON XML Syntax', 'is_correct': False})

print('  ✓ Lesson 3 + quiz')

l3_lab, _ = Lab.objects.get_or_create(
    lesson=les3,
    defaults={
        'title': 'JSX Superpowers',
        'description': 'Practice writing JSX with dynamic variables and ternary operators.',
        'instructions': 'Inside the `UserStatus` component, use curly braces to display the user`s `name`. Check their `isOnline` status and render "🟢 Online" if true, or "🔴 Offline" if false using a ternary operator.',
        'difficulty': 'medium',
        'xp_reward': 25,
        'objectives': [
            {'type': 'frontend_code', 'contains': '{', 'description': 'Use curly braces for JavaScript expressions'},
            {'type': 'frontend_code', 'contains': '?', 'description': 'Use a ternary operator'},
            {'type': 'frontend_render', 'contains': 'Online', 'description': 'Render the correct online status'},
        ],
        'hints': [
            'To display the name, simply write `{name}` inside your HTML.',
            'The ternary operator looks like this: `condition ? ifTrue : ifFalse`.',
            'Example: `Status: {isOnline ? "🟢 Online" : "🔴 Offline"}`'
        ],
        'flags': ['react_l3_flag'],
    }
)
print('  ✓ Lesson 3 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 4 — Props (Passing Data to Components)
# ═══════════════════════════════════════════════════════════════════════
L4_CONTENT = """## 🍳 Real-World Analogy

Imagine you're ordering a coffee. You tell the barista: "Medium latte with oat milk." The barista (component) takes your **order details** (props) and makes exactly what you asked for. Same barista, different orders, different coffees.

**Props** are the "order details" you pass to a component. They let you customize what a component displays without changing the component itself.

---

## 🧠 What are Props?

Props (short for "properties") are **inputs to a component**. They flow in one direction: **parent → child**. A component receives props and uses them to decide what to render.

### Key rules:
- Props are **read-only** — a component must never modify its own props
- Props flow **one way** — from parent to child, never the other way
- You can pass **anything** as a prop: strings, numbers, arrays, objects, even other components

---

## 💻 Code Example

```jsx
// The component receives props as a parameter
function CoffeeOrder({ size, milk, name }) {
  return (
    <div className="order-card">
      <h3>Order for: {name}</h3>
      <p>Size: {size}</p>
      <p>Milk: {milk}</p>
    </div>
  );
}

// Parent component passes different props each time
function CoffeeShop() {
  return (
    <div>
      <CoffeeOrder name="Alice" size="Large" milk="Oat" />
      <CoffeeOrder name="Bob" size="Small" milk="Whole" />
      <CoffeeOrder name="Carol" size="Medium" milk="Almond" />
    </div>
  );
}
```

Each `<CoffeeOrder />` gets different data through props but uses the same component template!

### Default props:

```jsx
function Button({ label = "Click me", color = "blue" }) {
  return (
    <button style={{ backgroundColor: color }}>
      {label}
    </button>
  );
}

// Uses defaults
<Button />

// Overrides defaults
<Button label="Submit" color="green" />
```

### Passing children:

```jsx
function Card({ children, title }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  );
}

<Card title="My Card">
  <p>This paragraph is the "children" prop!</p>
  <p>Anything between opening and closing tags.</p>
</Card>
```

---

## 🎮 Try It Yourself

Design a `StudentCard` component in your head. What props would it need? Maybe `name`, `grade`, `avatar`, `isOnline`. Think about which props should have defaults and which are required.

---

## 🔑 Key Takeaways

- Props are inputs you pass to components, like function arguments
- They flow one-way: parent → child
- Props are read-only — never modify them inside the component
- Destructure props in the function parameter for cleaner code
- Use default values for optional props
"""

les4, _ = Lesson.objects.get_or_create(
    module=mod1, slug='props-passing-data',
    defaults={
        'title': 'Props — Passing Data to Components',
        'content': L4_CONTENT,
        'content_type': 'text',
        'order': 4,
        'xp_reward': 15,
        'estimated_duration': 14,
    }
)

q4, _ = Quiz.objects.get_or_create(lesson=les4, defaults={
    'title': 'Props — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq4a, _ = QuizQuestion.objects.get_or_create(quiz=q4, order=1, defaults={
    'question_text': 'In which direction do props flow?',
    'question_type': 'single',
    'explanation': 'Props always flow one-way from parent components down to child components.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq4a, order=1, defaults={'answer_text': 'Child to parent', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq4a, order=2, defaults={'answer_text': 'Parent to child', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq4a, order=3, defaults={'answer_text': 'Both directions', 'is_correct': False})

qq4b, _ = QuizQuestion.objects.get_or_create(quiz=q4, order=2, defaults={
    'question_text': 'Can a component modify its own props?',
    'question_type': 'single',
    'explanation': 'Props are read-only. A component should never modify the props it receives.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq4b, order=1, defaults={'answer_text': 'Yes, always', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq4b, order=2, defaults={'answer_text': 'Only in useEffect', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq4b, order=3, defaults={'answer_text': 'No, props are read-only', 'is_correct': True})

qq4c, _ = QuizQuestion.objects.get_or_create(quiz=q4, order=3, defaults={
    'question_text': 'What is the "children" prop?',
    'question_type': 'single',
    'explanation': 'The children prop contains whatever JSX you place between the opening and closing tags of a component.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq4c, order=1, defaults={'answer_text': 'Content between opening and closing component tags', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq4c, order=2, defaults={'answer_text': 'A list of sub-components', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq4c, order=3, defaults={'answer_text': 'The component state', 'is_correct': False})

print('  ✓ Lesson 4 + quiz')

l4_lab, _ = Lab.objects.get_or_create(
    lesson=les4,
    defaults={
        'title': 'Passing Props',
        'description': 'Pass data down to child components using props.',
        'instructions': 'Create a `StudentCard` component that accepts `name` and `grade` props. Render two StudentCards inside App: one for "Alice" with grade "A", and one for "Bob" with grade "B".',
        'difficulty': 'medium',
        'xp_reward': 30,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'props', 'description': 'Use props (or destructure them)'},
            {'type': 'frontend_code', 'contains': 'name="Alice"', 'description': 'Pass "Alice" as a prop'},
            {'type': 'frontend_render', 'contains': 'Alice', 'description': 'Render Alice on the screen'},
            {'type': 'frontend_render', 'contains': 'Bob', 'description': 'Render Bob on the screen'},
        ],
        'hints': [
            'Your component should look like this: `function StudentCard(props) { ... }` or use destructuring `({ name, grade })`.',
            'When rendering the component, pass props like HTML attributes: `<StudentCard name="Alice" grade="A" />`.',
            'Make sure you have an `App` component that renders the two separate StudentCards and then ReactDOM.render(App).'
        ],
        'flags': ['react_l4_flag'],
    }
)
print('  ✓ Lesson 4 + lab')


# ═══════════════════════════════════════════════════════════════════════
#  MODULE 2: Interactivity & State
# ═══════════════════════════════════════════════════════════════════════
mod2, _ = Module.objects.get_or_create(
    course=react_course,
    order=2,
    defaults={
        'title': 'Interactivity & State',
        'description': 'Make your components interactive with state, events, conditional rendering, and lists.',
    }
)
print('✓ Module 2 ready')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 5 — useState (Component Memory)
# ═══════════════════════════════════════════════════════════════════════
L5_CONTENT = """## 🧠 Real-World Analogy

Imagine a **scoreboard** at a basketball game. The score changes every time a team scores, and the board updates instantly. The scoreboard *remembers* the current score — it doesn't reset every time you look at it.

**useState** is React's scoreboard — it lets your component **remember** a value and **update the screen** whenever that value changes.

---

## 🧠 What is State?

State is **data that can change over time**. Unlike props (which come from a parent and are read-only), state is **owned by the component itself** and can be updated.

### useState in 3 steps:

```jsx
import { useState } from 'react';

function Counter() {
  // 1. Declare state: [currentValue, setterFunction] = useState(initialValue)
  const [count, setCount] = useState(0);

  // 2. Use the value in JSX
  // 3. Update it with the setter function
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Add 1</button>
    </div>
  );
}
```

### How it works:
- `useState(0)` → creates a state variable starting at `0`
- `count` → the current value (read it, display it)
- `setCount` → the function to update it (ONLY way to change it)
- When you call `setCount(newValue)`, React **re-renders** the component with the new value

---

## 💻 More Examples

### Toggle example:
```jsx
function LightSwitch() {
  const [isOn, setIsOn] = useState(false);

  return (
    <div>
      <p>The light is {isOn ? "💡 ON" : "🌑 OFF"}</p>
      <button onClick={() => setIsOn(!isOn)}>
        {isOn ? "Turn Off" : "Turn On"}
      </button>
    </div>
  );
}
```

### Text input example:
```jsx
function NameTag() {
  const [name, setName] = useState("");

  return (
    <div>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Type your name"
      />
      <p>Hello, {name || "stranger"}!</p>
    </div>
  );
}
```

---

## ⚠️ Rules of useState

1. **Only call useState at the top level** of your component — not inside loops, conditions, or nested functions
2. **Never modify state directly** — always use the setter: `setCount(newVal)` ✅ not `count = newVal` ❌
3. State updates may be **batched** — React doesn't re-render after every single setState call

---

## 🔑 Key Takeaways

- `useState` lets a component remember and update data
- It returns `[value, setValue]` — a pair of current value and updater
- Calling the setter triggers a re-render
- State is private to each component instance
- Never mutate state directly — always use the setter function
"""

les5, _ = Lesson.objects.get_or_create(
    module=mod2, slug='usestate-component-memory',
    defaults={
        'title': 'useState — Component Memory',
        'content': L5_CONTENT,
        'content_type': 'text',
        'order': 1,
        'xp_reward': 20,
        'estimated_duration': 15,
    }
)

q5, _ = Quiz.objects.get_or_create(lesson=les5, defaults={
    'title': 'useState — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq5a, _ = QuizQuestion.objects.get_or_create(quiz=q5, order=1, defaults={
    'question_text': 'What does useState return?',
    'question_type': 'single',
    'explanation': 'useState returns an array with exactly two items: the current state value and a function to update it.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq5a, order=1, defaults={'answer_text': 'A single value', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq5a, order=2, defaults={'answer_text': 'An array: [value, setter]', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq5a, order=3, defaults={'answer_text': 'An object with .get() and .set()', 'is_correct': False})

qq5b, _ = QuizQuestion.objects.get_or_create(quiz=q5, order=2, defaults={
    'question_text': 'What happens when you call the setter function from useState?',
    'question_type': 'single',
    'explanation': 'Calling the setter function updates the state value and triggers React to re-render the component.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq5b, order=1, defaults={'answer_text': 'Nothing visible happens', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq5b, order=2, defaults={'answer_text': 'The page fully reloads', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq5b, order=3, defaults={'answer_text': 'React re-renders the component with the new value', 'is_correct': True})

qq5c, _ = QuizQuestion.objects.get_or_create(quiz=q5, order=3, defaults={
    'question_text': 'Where should you call useState inside a component?',
    'question_type': 'single',
    'explanation': 'useState must be called at the top level of your component, not inside loops, conditions, or nested functions.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq5c, order=1, defaults={'answer_text': 'Inside a for loop', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq5c, order=2, defaults={'answer_text': 'At the top level of the component', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq5c, order=3, defaults={'answer_text': 'Inside an if statement', 'is_correct': False})

print('  ✓ Lesson 5 + quiz')

l5_lab, _ = Lab.objects.get_or_create(
    lesson=les5,
    defaults={
        'title': 'Build a Counter',
        'description': 'Create a simple counter with increment and decrement buttons using useState.',
        'instructions': '1. Import useState from React.\\n2. Create a Counter component with a state variable `count` starting at 0.\\n3. Add an "Increment" button that increases count by 1.\\n4. Display the current count in a <p> tag.',
        'difficulty': 'easy',
        'xp_reward': 25,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'useState', 'description': 'Use the useState hook'},
            {'type': 'frontend_code', 'contains': 'setCount', 'description': 'Use a state setter function'},
            {'type': 'frontend_render', 'contains': '0', 'description': 'Display the initial count of 0'},
        ],
        'hints': [
            'Start with: `const [count, setCount] = React.useState(0);`',
            'Your button should look like: `<button onClick={() => setCount(count + 1)}>Increment</button>`',
            'Display the count: `<p>Count: {count}</p>`'
        ],
        'flags': ['react_l5_flag'],
    }
)
print('  ✓ Lesson 5 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 6 — Event Handling
# ═══════════════════════════════════════════════════════════════════════
L6_CONTENT = """## 🎯 Real-World Analogy

Think about a **doorbell**. When someone presses it → a sound plays. The press is the **event**, and the sound is the **handler** (the response).

In React, it works the same way:
- **Event** = user does something (click, type, hover, submit)
- **Handler** = your function that runs in response

---

## 🧠 How Events Work in React

React events look similar to HTML events but with key differences:

| HTML | React |
|------|-------|
| `onclick="handleClick()"` | `onClick={handleClick}` |
| lowercase | camelCase |
| string | function reference |

### The basics:

```jsx
function AlertButton() {
  function handleClick() {
    alert("You clicked me! 🎉");
  }

  return <button onClick={handleClick}>Click Me</button>;
}
```

**Important:** Pass the function *reference*, not a function *call*:
- ✅ `onClick={handleClick}` — passes the function
- ❌ `onClick={handleClick()}` — CALLS it immediately on render!

---

## 💻 Common Event Patterns

### onClick — Button clicks:
```jsx
function LikeButton() {
  const [likes, setLikes] = useState(0);

  return (
    <button onClick={() => setLikes(likes + 1)}>
      ❤️ {likes} Likes
    </button>
  );
}
```

### onChange — Input typing:
```jsx
function SearchBar() {
  const [query, setQuery] = useState("");

  function handleChange(event) {
    setQuery(event.target.value);
  }

  return (
    <div>
      <input onChange={handleChange} placeholder="Search..." />
      <p>Searching for: {query}</p>
    </div>
  );
}
```

### onSubmit — Form submission:
```jsx
function LoginForm() {
  function handleSubmit(event) {
    event.preventDefault(); // Stop the page from reloading!
    alert("Form submitted!");
  }

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Username" />
      <button type="submit">Log In</button>
    </form>
  );
}
```

### Passing arguments to handlers:
```jsx
function FruitList() {
  function handleClick(fruit) {
    alert(`You picked: ${fruit}`);
  }

  return (
    <div>
      <button onClick={() => handleClick("Apple")}>🍎 Apple</button>
      <button onClick={() => handleClick("Banana")}>🍌 Banana</button>
    </div>
  );
}
```

---

## 🔑 Key Takeaways

- React events use camelCase: `onClick`, `onChange`, `onSubmit`
- Pass the function *reference*, not a function *call*
- Use `event.preventDefault()` to stop default browser behavior
- The `event` object gives you info about what happened (e.g., `event.target.value`)
- Wrap handlers in arrow functions when you need to pass arguments
"""

les6, _ = Lesson.objects.get_or_create(
    module=mod2, slug='event-handling',
    defaults={
        'title': 'Event Handling',
        'content': L6_CONTENT,
        'content_type': 'text',
        'order': 2,
        'xp_reward': 20,
        'estimated_duration': 14,
    }
)

q6, _ = Quiz.objects.get_or_create(lesson=les6, defaults={
    'title': 'Event Handling — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq6a, _ = QuizQuestion.objects.get_or_create(quiz=q6, order=1, defaults={
    'question_text': 'How do you attach a click handler in React?',
    'question_type': 'single',
    'explanation': 'React uses camelCase event names and passes a function reference, not a string.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq6a, order=1, defaults={'answer_text': 'onclick="handleClick()"', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq6a, order=2, defaults={'answer_text': 'onClick={handleClick}', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq6a, order=3, defaults={'answer_text': 'click={handleClick}', 'is_correct': False})

qq6b, _ = QuizQuestion.objects.get_or_create(quiz=q6, order=2, defaults={
    'question_text': 'What does event.preventDefault() do?',
    'question_type': 'single',
    'explanation': 'event.preventDefault() stops the browser from performing its default action, like reloading the page on form submission.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq6b, order=1, defaults={'answer_text': 'Stops the component from rendering', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq6b, order=2, defaults={'answer_text': 'Prevents the default browser behavior', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq6b, order=3, defaults={'answer_text': 'Deletes the event listener', 'is_correct': False})

qq6c, _ = QuizQuestion.objects.get_or_create(quiz=q6, order=3, defaults={
    'question_text': 'What is wrong with onClick={handleClick()}?',
    'question_type': 'single',
    'explanation': 'Adding parentheses calls the function immediately during render instead of waiting for the click.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq6c, order=1, defaults={'answer_text': 'Nothing, it works fine', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq6c, order=2, defaults={'answer_text': 'It calls the function immediately instead of on click', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq6c, order=3, defaults={'answer_text': 'It causes a syntax error', 'is_correct': False})

print('  ✓ Lesson 6 + quiz')

l6_lab, _ = Lab.objects.get_or_create(
    lesson=les6,
    defaults={
        'title': 'Interactive Buttons',
        'description': 'Build a component with buttons that respond to clicks and show alerts.',
        'instructions': '1. Create a ColorPicker component.\\n2. Add three buttons labeled "Red", "Green", and "Blue".\\n3. When a button is clicked, update a state variable to store the chosen color.\\n4. Display the chosen color name on screen.',
        'difficulty': 'medium',
        'xp_reward': 30,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'onClick', 'description': 'Use an onClick event handler'},
            {'type': 'frontend_code', 'contains': 'useState', 'description': 'Use useState to track the color'},
            {'type': 'frontend_render', 'contains': 'Red', 'description': 'Show a Red button'},
        ],
        'hints': [
            'Start with `const [color, setColor] = React.useState("none");` to track the selected color.',
            'Each button should call setColor: `<button onClick={() => setColor("Red")}>Red</button>`',
            'Display the color: `<p>Selected color: {color}</p>`'
        ],
        'flags': ['react_l6_flag'],
    }
)
print('  ✓ Lesson 6 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 7 — Conditional Rendering
# ═══════════════════════════════════════════════════════════════════════
L7_CONTENT = """## 🚦 Real-World Analogy

Think about a **traffic light**. Red means stop, green means go. The light *conditionally* shows a different signal depending on the current state.

React works the same way — you can **show or hide** parts of your UI based on conditions. Logged in? Show the dashboard. Not logged in? Show the login form.

---

## 🧠 How to Conditionally Render

### Method 1: Ternary Operator (inline if/else)
```jsx
function Greeting({ isLoggedIn }) {
  return (
    <div>
      {isLoggedIn ? <h1>Welcome back! 👋</h1> : <h1>Please sign in</h1>}
    </div>
  );
}
```

### Method 2: Logical AND `&&` (show or nothing)
```jsx
function Notification({ hasMessages, count }) {
  return (
    <div>
      <h1>Dashboard</h1>
      {hasMessages && <p>You have {count} new messages! 📬</p>}
    </div>
  );
}
```
If `hasMessages` is true → shows the `<p>`. If false → shows nothing.

### Method 3: Early return
```jsx
function AdminPanel({ isAdmin }) {
  if (!isAdmin) {
    return <p>Access denied ⛔</p>;
  }

  return (
    <div>
      <h1>Admin Dashboard</h1>
      <p>Welcome, admin!</p>
    </div>
  );
}
```

---

## 💻 Full Example: Toggle Visibility

```jsx
function SecretMessage() {
  const [show, setShow] = useState(false);

  return (
    <div>
      <button onClick={() => setShow(!show)}>
        {show ? "Hide" : "Show"} Secret
      </button>
      {show && <p>🤫 React is awesome!</p>}
    </div>
  );
}
```

### Rendering different components:
```jsx
function Page({ userRole }) {
  function renderContent() {
    switch (userRole) {
      case "admin": return <AdminDashboard />;
      case "user": return <UserDashboard />;
      default: return <LoginPage />;
    }
  }

  return <div>{renderContent()}</div>;
}
```

---

## ⚠️ Common Gotcha

Watch out with `&&` and numbers!

```jsx
// ❌ Bug: renders "0" on screen when count is 0
{count && <p>You have {count} items</p>}

// ✅ Fix: convert to boolean first
{count > 0 && <p>You have {count} items</p>}
```

---

## 🔑 Key Takeaways

- Use **ternary** `? :` for if/else rendering
- Use **&&** for show-or-nothing rendering
- Use **early return** for guard clauses
- Be careful with `&&` and falsy values like `0`
- Conditional rendering is just JavaScript — no special syntax!
"""

les7, _ = Lesson.objects.get_or_create(
    module=mod2, slug='conditional-rendering',
    defaults={
        'title': 'Conditional Rendering',
        'content': L7_CONTENT,
        'content_type': 'text',
        'order': 3,
        'xp_reward': 20,
        'estimated_duration': 12,
    }
)

q7, _ = Quiz.objects.get_or_create(lesson=les7, defaults={
    'title': 'Conditional Rendering — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq7a, _ = QuizQuestion.objects.get_or_create(quiz=q7, order=1, defaults={
    'question_text': 'Which operator shows content OR nothing (not an else)?',
    'question_type': 'single',
    'explanation': 'The logical AND (&&) operator renders the content if the condition is true, otherwise renders nothing.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq7a, order=1, defaults={'answer_text': 'Ternary ? :', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq7a, order=2, defaults={'answer_text': 'Logical AND &&', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq7a, order=3, defaults={'answer_text': 'if/else statement', 'is_correct': False})

qq7b, _ = QuizQuestion.objects.get_or_create(quiz=q7, order=2, defaults={
    'question_text': 'What will {0 && <p>Hello</p>} render?',
    'question_type': 'single',
    'explanation': '0 is a falsy value in JavaScript. With &&, React will render 0 on screen because it is a valid JSX number, not nothing.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq7b, order=1, defaults={'answer_text': 'Nothing', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq7b, order=2, defaults={'answer_text': 'The number 0', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq7b, order=3, defaults={'answer_text': '<p>Hello</p>', 'is_correct': False})

qq7c, _ = QuizQuestion.objects.get_or_create(quiz=q7, order=3, defaults={
    'question_text': 'When should you use an early return in a component?',
    'question_type': 'single',
    'explanation': 'Early returns are great for guard clauses — quickly handling edge cases before the main render logic.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq7c, order=1, defaults={'answer_text': 'To handle guard clauses or edge cases', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq7c, order=2, defaults={'answer_text': 'To make the code longer', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq7c, order=3, defaults={'answer_text': 'To prevent React from rendering at all', 'is_correct': False})

print('  ✓ Lesson 7 + quiz')

l7_lab, _ = Lab.objects.get_or_create(
    lesson=les7,
    defaults={
        'title': 'Show / Hide Toggle',
        'description': 'Build a toggle that shows and hides a secret message.',
        'instructions': '1. Create a SecretToggle component.\\n2. Use useState to track a boolean called `visible`.\\n3. Add a button that toggles `visible` between true and false.\\n4. When visible is true, show a paragraph with the text "The secret is React rocks!". When false, hide it.',
        'difficulty': 'easy',
        'xp_reward': 25,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'useState', 'description': 'Use useState for visibility state'},
            {'type': 'frontend_code', 'contains': '&&', 'description': 'Use && or ternary for conditional rendering'},
            {'type': 'frontend_code', 'contains': 'onClick', 'description': 'Toggle visibility on click'},
        ],
        'hints': [
            'Start with `const [visible, setVisible] = React.useState(false);`',
            'Toggle with: `<button onClick={() => setVisible(!visible)}>Toggle</button>`',
            'Conditionally render: `{visible && <p>The secret is React rocks!</p>}`'
        ],
        'flags': ['react_l7_flag'],
    }
)
print('  ✓ Lesson 7 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 8 — Lists & .map() (Rendering Arrays)
# ═══════════════════════════════════════════════════════════════════════
L8_CONTENT = """## 📋 Real-World Analogy

Imagine you have a **guest list** for a party. Instead of writing each invitation card by hand, you use a **template** and just swap the name for each guest. Same card design, different names.

React's `.map()` method does exactly this — it takes an array of data and generates a list of components from a template.

---

## 🧠 Rendering Lists with .map()

```jsx
function GuestList() {
  const guests = ["Alice", "Bob", "Carol", "Dave"];

  return (
    <ul>
      {guests.map((name) => (
        <li key={name}>{name}</li>
      ))}
    </ul>
  );
}
```

### Breaking it down:
1. `guests.map(...)` → loops through every item in the array
2. For each item, it returns a piece of JSX
3. `key={name}` → helps React track which items changed (REQUIRED!)

---

## 🔑 The `key` Prop — Why It Matters

React needs a **unique key** for each list item to efficiently update the DOM.

```jsx
// ✅ Good keys — unique and stable
{users.map(user => (
  <UserCard key={user.id} name={user.name} />
))}

// ❌ Bad keys — array index (can cause bugs)
{users.map((user, index) => (
  <UserCard key={index} name={user.name} />
))}
```

**Use** the item's unique ID as the key when possible. Only use the array index as a last resort.

---

## 💻 Full Example: Todo List

```jsx
function TodoApp() {
  const [todos, setTodos] = useState([
    { id: 1, text: "Learn React", done: false },
    { id: 2, text: "Build a project", done: false },
    { id: 3, text: "Get hired", done: false },
  ]);

  function toggleTodo(id) {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, done: !todo.done } : todo
    ));
  }

  return (
    <ul>
      {todos.map(todo => (
        <li
          key={todo.id}
          onClick={() => toggleTodo(todo.id)}
          style={{ textDecoration: todo.done ? "line-through" : "none" }}
        >
          {todo.text} {todo.done ? "✅" : "⬜"}
        </li>
      ))}
    </ul>
  );
}
```

### Rendering objects:
```jsx
const products = [
  { id: 1, name: "Laptop", price: 999 },
  { id: 2, name: "Phone", price: 699 },
  { id: 3, name: "Tablet", price: 499 },
];

function ProductList() {
  return (
    <div>
      {products.map(product => (
        <div key={product.id} className="product-card">
          <h3>{product.name}</h3>
          <p>${product.price}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes

```jsx
// ❌ Forgetting the key prop — React will warn you
{items.map(item => <li>{item}</li>)}

// ❌ Forgetting to return JSX inside map
{items.map(item => {
  <li>{item}</li>  // Missing return!
})}

// ✅ Either use arrow shorthand (implicit return)
{items.map(item => <li key={item}>{item}</li>)}

// ✅ Or add explicit return with curly braces
{items.map(item => {
  return <li key={item}>{item}</li>;
})}
```

---

## 🔑 Key Takeaways

- Use `.map()` to render arrays of data as JSX
- Every list item needs a unique `key` prop
- Prefer stable IDs over array indexes for keys
- Use implicit return `(...)` or explicit `return` inside map
- You can render any data shape — strings, objects, nested arrays
"""

les8, _ = Lesson.objects.get_or_create(
    module=mod2, slug='lists-and-map',
    defaults={
        'title': 'Lists & .map() — Rendering Arrays',
        'content': L8_CONTENT,
        'content_type': 'text',
        'order': 4,
        'xp_reward': 20,
        'estimated_duration': 14,
    }
)

q8, _ = Quiz.objects.get_or_create(lesson=les8, defaults={
    'title': 'Lists & .map() — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq8a, _ = QuizQuestion.objects.get_or_create(quiz=q8, order=1, defaults={
    'question_text': 'Why does React require a "key" prop on list items?',
    'question_type': 'single',
    'explanation': 'Keys help React identify which items have changed, been added, or removed, making updates efficient.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq8a, order=1, defaults={'answer_text': 'For CSS styling', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq8a, order=2, defaults={'answer_text': 'To efficiently track and update list items', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq8a, order=3, defaults={'answer_text': 'To sort the list alphabetically', 'is_correct': False})

qq8b, _ = QuizQuestion.objects.get_or_create(quiz=q8, order=2, defaults={
    'question_text': 'What JavaScript method do you use to render a list in React?',
    'question_type': 'single',
    'explanation': '.map() transforms each item in an array into a JSX element.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq8b, order=1, defaults={'answer_text': '.forEach()', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq8b, order=2, defaults={'answer_text': '.map()', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq8b, order=3, defaults={'answer_text': '.filter()', 'is_correct': False})

qq8c, _ = QuizQuestion.objects.get_or_create(quiz=q8, order=3, defaults={
    'question_text': 'What is the best value to use as a key?',
    'question_type': 'single',
    'explanation': 'A unique, stable ID is the best key. Array indexes can cause bugs when the list order changes.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq8c, order=1, defaults={'answer_text': 'The array index', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq8c, order=2, defaults={'answer_text': 'A random number', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq8c, order=3, defaults={'answer_text': "A unique ID from the data", 'is_correct': True})

print('  ✓ Lesson 8 + quiz')

l8_lab, _ = Lab.objects.get_or_create(
    lesson=les8,
    defaults={
        'title': 'Fruit List',
        'description': 'Render a list of fruits using .map() with proper keys.',
        'instructions': '1. Create a FruitList component.\\n2. Define an array of fruits: ["Apple", "Banana", "Cherry", "Mango"].\\n3. Use .map() to render each fruit inside an <li> element.\\n4. Add a unique key to each <li>.',
        'difficulty': 'easy',
        'xp_reward': 25,
        'objectives': [
            {'type': 'frontend_code', 'contains': '.map(', 'description': 'Use the .map() method'},
            {'type': 'frontend_code', 'contains': 'key=', 'description': 'Provide a key prop'},
            {'type': 'frontend_render', 'contains': 'Apple', 'description': 'Render Apple in the list'},
            {'type': 'frontend_render', 'contains': 'Banana', 'description': 'Render Banana in the list'},
        ],
        'hints': [
            'Define your array: `const fruits = ["Apple", "Banana", "Cherry", "Mango"];`',
            'Map over it: `{fruits.map(fruit => <li key={fruit}>{fruit}</li>)}`',
            'Wrap everything in a `<ul>` tag for proper HTML list structure.'
        ],
        'flags': ['react_l8_flag'],
    }
)
print('  ✓ Lesson 8 + lab')


# ═══════════════════════════════════════════════════════════════════════
#  MODULE 3: Data Flow & Effects
# ═══════════════════════════════════════════════════════════════════════
mod3, _ = Module.objects.get_or_create(
    course=react_course,
    order=3,
    defaults={
        'title': 'Data Flow & Effects',
        'description': 'Handle side effects, build forms, share state between components, and reference DOM elements.',
    }
)
print('✓ Module 3 ready')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 9 — useEffect (Side Effects)
# ═══════════════════════════════════════════════════════════════════════
L9_CONTENT = """## ⏰ Real-World Analogy

Imagine you have a **smart home assistant**. You set a rule: "Every time I walk through the front door, turn on the lights." The rule doesn't change the door — it triggers a **side effect** (turning on lights) in response to an event.

**useEffect** is your component's smart assistant — it runs code **after** React renders your component. Perfect for things that happen "outside" of rendering: fetching data, setting up timers, updating the page title, etc.

---

## 🧠 What is useEffect?

A **side effect** is anything that reaches outside your component:
- Fetching data from an API
- Setting up a timer or interval
- Updating the document title
- Adding/removing event listeners
- Saving to localStorage

### Basic syntax:

```jsx
import { useState, useEffect } from 'react';

function MyComponent() {
  const [count, setCount] = useState(0);

  // Runs AFTER every render
  useEffect(() => {
    document.title = `You clicked ${count} times`;
  });

  return <button onClick={() => setCount(count + 1)}>Click me</button>;
}
```

---

## 💻 The Dependency Array

The second argument to useEffect controls **when** it runs:

```jsx
// 1. Runs after EVERY render (no array)
useEffect(() => {
  console.log("I run after every render");
});

// 2. Runs ONLY ONCE on mount (empty array)
useEffect(() => {
  console.log("I run once when component mounts");
}, []);

// 3. Runs when specific values change
useEffect(() => {
  console.log(`Count changed to: ${count}`);
}, [count]);
```

### Fetching data example:
```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`https://api.example.com/users/${userId}`)
      .then(res => res.json())
      .then(data => {
        setUser(data);
        setLoading(false);
      });
  }, [userId]); // Re-fetch when userId changes

  if (loading) return <p>Loading...</p>;
  return <h1>{user.name}</h1>;
}
```

---

## 🧹 Cleanup Functions

Some effects need **cleanup** — like removing event listeners or clearing timers:

```jsx
function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds(s => s + 1);
    }, 1000);

    // Cleanup: runs when component unmounts
    return () => clearInterval(interval);
  }, []);

  return <p>Timer: {seconds}s</p>;
}
```

The cleanup function prevents **memory leaks** when your component is removed from the page.

---

## 🔑 Key Takeaways

- useEffect runs code **after** rendering
- The dependency array controls when the effect re-runs
- `[]` = run once on mount, `[dep]` = run when dep changes
- Return a cleanup function for timers, listeners, subscriptions
- Don't forget to include all variables used in the effect in the dependency array
"""

les9, _ = Lesson.objects.get_or_create(
    module=mod3, slug='useeffect-side-effects',
    defaults={
        'title': 'useEffect — Side Effects',
        'content': L9_CONTENT,
        'content_type': 'text',
        'order': 1,
        'xp_reward': 25,
        'estimated_duration': 16,
    }
)

q9, _ = Quiz.objects.get_or_create(lesson=les9, defaults={
    'title': 'useEffect — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq9a, _ = QuizQuestion.objects.get_or_create(quiz=q9, order=1, defaults={
    'question_text': 'When does useEffect with an empty dependency array [] run?',
    'question_type': 'single',
    'explanation': 'An empty dependency array tells useEffect to run only once, after the initial render (mount).',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq9a, order=1, defaults={'answer_text': 'After every render', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq9a, order=2, defaults={'answer_text': 'Only once after the first render', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq9a, order=3, defaults={'answer_text': 'Before the component renders', 'is_correct': False})

qq9b, _ = QuizQuestion.objects.get_or_create(quiz=q9, order=2, defaults={
    'question_text': 'What is the purpose of the cleanup function returned from useEffect?',
    'question_type': 'single',
    'explanation': 'The cleanup function runs when the component unmounts or before the effect re-runs, preventing memory leaks.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq9b, order=1, defaults={'answer_text': 'To reset the component state', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq9b, order=2, defaults={'answer_text': 'To prevent memory leaks by cleaning up resources', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq9b, order=3, defaults={'answer_text': 'To re-render the component', 'is_correct': False})

qq9c, _ = QuizQuestion.objects.get_or_create(quiz=q9, order=3, defaults={
    'question_text': 'Which of these is a side effect?',
    'question_type': 'single',
    'explanation': 'Fetching data from an API is a side effect because it reaches outside the component to interact with external systems.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq9c, order=1, defaults={'answer_text': 'Returning JSX', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq9c, order=2, defaults={'answer_text': 'Declaring a variable', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq9c, order=3, defaults={'answer_text': 'Fetching data from an API', 'is_correct': True})

print('  ✓ Lesson 9 + quiz')

l9_lab, _ = Lab.objects.get_or_create(
    lesson=les9,
    defaults={
        'title': 'Document Title Updater',
        'description': 'Use useEffect to update the browser tab title when a counter changes.',
        'instructions': '1. Create a TitleUpdater component with a count state starting at 0.\\n2. Add a button to increment the count.\\n3. Use useEffect to update document.title to show the current count.\\n4. Display the count on screen.',
        'difficulty': 'medium',
        'xp_reward': 30,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'useEffect', 'description': 'Use the useEffect hook'},
            {'type': 'frontend_code', 'contains': 'document.title', 'description': 'Update document.title inside useEffect'},
            {'type': 'frontend_code', 'contains': 'useState', 'description': 'Track the count with useState'},
        ],
        'hints': [
            'Start with `const [count, setCount] = React.useState(0);`',
            'Add useEffect: `React.useEffect(() => { document.title = \\`Count: ${count}\\`; }, [count]);`',
            'Display and increment: `<button onClick={() => setCount(count + 1)}>Count: {count}</button>`'
        ],
        'flags': ['react_l9_flag'],
    }
)
print('  ✓ Lesson 9 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 10 — Forms in React
# ═══════════════════════════════════════════════════════════════════════
L10_CONTENT = """## 📝 Real-World Analogy

Think of a **waiter taking your order**. As you speak, the waiter writes everything down on a notepad in real time. The notepad always reflects your latest order — if you change your mind, the waiter updates the notepad immediately.

In React, **controlled inputs** work the same way. React's state is the notepad, and every keystroke updates it in real time.

---

## 🧠 Controlled vs Uncontrolled Inputs

### Controlled Input (React way ✅):
React state is the "single source of truth" — the input's value always matches state.

```jsx
function ControlledInput() {
  const [name, setName] = useState("");

  return (
    <input
      value={name}
      onChange={(e) => setName(e.target.value)}
    />
  );
}
```

### Why controlled?
- You always know the current value
- You can validate, format, or restrict input in real time
- Easy to reset, submit, or share the value

---

## 💻 Building a Complete Form

```jsx
function SignupForm() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    console.log("Submitted:", formData);
    alert(`Welcome, ${formData.username}!`);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="username"
        value={formData.username}
        onChange={handleChange}
        placeholder="Username"
      />
      <input
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Email"
      />
      <input
        name="password"
        type="password"
        value={formData.password}
        onChange={handleChange}
        placeholder="Password"
      />
      <button type="submit">Sign Up</button>
    </form>
  );
}
```

### Key pattern: One handler for multiple inputs
Using `[name]: value` with dynamic property names means a single `handleChange` function works for ALL inputs!

---

## 🎛️ Other Input Types

### Checkbox:
```jsx
const [agreed, setAgreed] = useState(false);

<input
  type="checkbox"
  checked={agreed}
  onChange={(e) => setAgreed(e.target.checked)}
/>
```

### Select dropdown:
```jsx
const [color, setColor] = useState("red");

<select value={color} onChange={(e) => setColor(e.target.value)}>
  <option value="red">Red</option>
  <option value="blue">Blue</option>
  <option value="green">Green</option>
</select>
```

### Textarea:
```jsx
const [bio, setBio] = useState("");

<textarea value={bio} onChange={(e) => setBio(e.target.value)} />
```

---

## ✅ Form Validation

```jsx
function ValidatedForm() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!email.includes("@")) {
      setError("Please enter a valid email");
      return;
    }
    setError("");
    alert("Form submitted!");
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      {error && <p style={{color: 'red'}}>{error}</p>}
      <button type="submit">Submit</button>
    </form>
  );
}
```

---

## 🔑 Key Takeaways

- Controlled inputs keep their value in React state
- Use `onChange` to update state on every keystroke
- Use `e.preventDefault()` in `onSubmit` to stop page reload
- Handle multiple inputs with a single handler using `[name]: value`
- Validate before submitting and show error messages
"""

les10, _ = Lesson.objects.get_or_create(
    module=mod3, slug='forms-in-react',
    defaults={
        'title': 'Forms in React',
        'content': L10_CONTENT,
        'content_type': 'text',
        'order': 2,
        'xp_reward': 25,
        'estimated_duration': 15,
    }
)

q10, _ = Quiz.objects.get_or_create(lesson=les10, defaults={
    'title': 'Forms in React — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq10a, _ = QuizQuestion.objects.get_or_create(quiz=q10, order=1, defaults={
    'question_text': 'What makes an input "controlled" in React?',
    'question_type': 'single',
    'explanation': 'A controlled input has its value managed by React state, making state the single source of truth.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq10a, order=1, defaults={'answer_text': 'It has a CSS class applied', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq10a, order=2, defaults={'answer_text': 'Its value is linked to React state', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq10a, order=3, defaults={'answer_text': 'It uses the required attribute', 'is_correct': False})

qq10b, _ = QuizQuestion.objects.get_or_create(quiz=q10, order=2, defaults={
    'question_text': 'Why do we call e.preventDefault() in a form submit handler?',
    'question_type': 'single',
    'explanation': 'By default, submitting a form causes a full page reload. preventDefault stops that so React can handle it.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq10b, order=1, defaults={'answer_text': 'To clear the form fields', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq10b, order=2, defaults={'answer_text': 'To prevent the page from reloading', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq10b, order=3, defaults={'answer_text': 'To validate the form data', 'is_correct': False})

qq10c, _ = QuizQuestion.objects.get_or_create(quiz=q10, order=3, defaults={
    'question_text': 'How do you handle multiple form inputs with one handler?',
    'question_type': 'single',
    'explanation': 'Using the input name attribute with computed property syntax [name]: value lets one handler update any field.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq10c, order=1, defaults={'answer_text': 'Create a separate handler for each input', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq10c, order=2, defaults={'answer_text': 'Use the name attribute with [name]: value', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq10c, order=3, defaults={'answer_text': 'Use a for loop inside the handler', 'is_correct': False})

print('  ✓ Lesson 10 + quiz')

l10_lab, _ = Lab.objects.get_or_create(
    lesson=les10,
    defaults={
        'title': 'Contact Form',
        'description': 'Build a controlled contact form with name and message fields.',
        'instructions': '1. Create a ContactForm component.\\n2. Use useState to track a `name` and `message` field.\\n3. Create controlled `<input>` for name and `<textarea>` for message.\\n4. On submit, display an alert showing the submitted name and message.',
        'difficulty': 'medium',
        'xp_reward': 30,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'onChange', 'description': 'Use onChange to update state'},
            {'type': 'frontend_code', 'contains': 'onSubmit', 'description': 'Handle form submission'},
            {'type': 'frontend_code', 'contains': 'value=', 'description': 'Bind input value to state'},
        ],
        'hints': [
            'Track two state variables: `const [name, setName] = React.useState(""); const [message, setMessage] = React.useState("");`',
            'The input should look like: `<input value={name} onChange={(e) => setName(e.target.value)} />`',
            'Add `<form onSubmit={(e) => { e.preventDefault(); alert(name + ": " + message); }}>` around your inputs.'
        ],
        'flags': ['react_l10_flag'],
    }
)
print('  ✓ Lesson 10 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 11 — Lifting State Up
# ═══════════════════════════════════════════════════════════════════════
L11_CONTENT = """## 🏗️ Real-World Analogy

Imagine two walkie-talkies. They can't talk directly to each other — they both connect through a **shared radio frequency** (a common channel). If one sends a message, the other receives it through that shared channel.

In React, when two sibling components need to share data, they can't talk directly. Instead, you **lift the state up** to their common parent — the parent becomes the "radio frequency" that coordinates them.

---

## 🧠 The Problem

```jsx
// ❌ These siblings can't share data!
function TemperatureInput() {
  const [temp, setTemp] = useState(""); // Each has its OWN state
  return <input value={temp} onChange={e => setTemp(e.target.value)} />;
}

function App() {
  return (
    <div>
      <TemperatureInput /> {/* Celsius */}
      <TemperatureInput /> {/* Fahrenheit */}
      {/* How do we keep these in sync? */}
    </div>
  );
}
```

## ✅ The Solution: Lift State Up

Move the shared state to the **closest common parent**:

```jsx
function TemperatureInput({ label, value, onChange }) {
  return (
    <div>
      <label>{label}</label>
      <input value={value} onChange={e => onChange(e.target.value)} />
    </div>
  );
}

function TemperatureConverter() {
  const [celsius, setCelsius] = useState("");

  const fahrenheit = celsius ? (parseFloat(celsius) * 9/5 + 32).toFixed(1) : "";

  return (
    <div>
      <TemperatureInput
        label="Celsius"
        value={celsius}
        onChange={setCelsius}
      />
      <TemperatureInput
        label="Fahrenheit"
        value={fahrenheit}
        onChange={f => setCelsius(((parseFloat(f) - 32) * 5/9).toFixed(1))}
      />
    </div>
  );
}
```

---

## 💻 Common Pattern: Sibling Communication

```jsx
function SearchBar({ query, onQueryChange }) {
  return (
    <input
      value={query}
      onChange={e => onQueryChange(e.target.value)}
      placeholder="Search products..."
    />
  );
}

function ProductList({ query }) {
  const products = ["Laptop", "Phone", "Tablet", "Watch"];
  const filtered = products.filter(p =>
    p.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <ul>
      {filtered.map(p => <li key={p}>{p}</li>)}
    </ul>
  );
}

function App() {
  const [query, setQuery] = useState("");

  return (
    <div>
      <SearchBar query={query} onQueryChange={setQuery} />
      <ProductList query={query} />
    </div>
  );
}
```

Both `SearchBar` and `ProductList` share the `query` state through their parent `App`.

---

## 📐 When to Lift State

Ask yourself: **"Does more than one component need this data?"**
- **Yes** → lift it to their closest common parent
- **No** → keep it local in the component that needs it

### The pattern:
1. Remove state from child components
2. Move it to the closest common parent
3. Pass the value down via props
4. Pass the updater function down via props

---

## 🔑 Key Takeaways

- When siblings need to share state, lift it to their common parent
- The parent owns the state and passes values + updaters as props
- Data flows down through props, events flow up through callback functions
- Only lift state when multiple components need the same data
- This is the foundation of React's "one-way data flow"
"""

les11, _ = Lesson.objects.get_or_create(
    module=mod3, slug='lifting-state-up',
    defaults={
        'title': 'Lifting State Up',
        'content': L11_CONTENT,
        'content_type': 'text',
        'order': 3,
        'xp_reward': 25,
        'estimated_duration': 14,
    }
)

q11, _ = Quiz.objects.get_or_create(lesson=les11, defaults={
    'title': 'Lifting State Up — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq11a, _ = QuizQuestion.objects.get_or_create(quiz=q11, order=1, defaults={
    'question_text': 'When should you lift state up?',
    'question_type': 'single',
    'explanation': 'Lift state up when multiple sibling components need to share or react to the same piece of data.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq11a, order=1, defaults={'answer_text': 'When a single component needs the data', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq11a, order=2, defaults={'answer_text': 'When multiple components need to share the same data', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq11a, order=3, defaults={'answer_text': 'Always, for every piece of state', 'is_correct': False})

qq11b, _ = QuizQuestion.objects.get_or_create(quiz=q11, order=2, defaults={
    'question_text': 'Where does the shared state live after lifting it up?',
    'question_type': 'single',
    'explanation': 'The state is moved to the closest common parent of the components that need it.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq11b, order=1, defaults={'answer_text': 'In a global variable', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq11b, order=2, defaults={'answer_text': 'In the closest common parent component', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq11b, order=3, defaults={'answer_text': 'In localStorage', 'is_correct': False})

qq11c, _ = QuizQuestion.objects.get_or_create(quiz=q11, order=3, defaults={
    'question_text': 'How do child components update lifted state?',
    'question_type': 'single',
    'explanation': 'The parent passes the state updater function as a prop callback, which children call to request updates.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq11c, order=1, defaults={'answer_text': 'They modify props directly', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq11c, order=2, defaults={'answer_text': 'Through callback functions passed as props', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq11c, order=3, defaults={'answer_text': 'Using document.getElementById', 'is_correct': False})

print('  ✓ Lesson 11 + quiz')

l11_lab, _ = Lab.objects.get_or_create(
    lesson=les11,
    defaults={
        'title': 'Synced Inputs',
        'description': 'Build two inputs that stay in sync by lifting state to their parent.',
        'instructions': '1. Create a parent App component that owns a `text` state.\\n2. Create a MirrorInput component that receives `value` and `onChange` as props.\\n3. Render two MirrorInput components.\\n4. Whatever the user types in one input should appear in the other instantly.',
        'difficulty': 'medium',
        'xp_reward': 35,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'props', 'description': 'Child component receives data via props'},
            {'type': 'frontend_code', 'contains': 'onChange', 'description': 'Pass an onChange callback from parent'},
            {'type': 'frontend_code', 'contains': 'useState', 'description': 'State lives in the parent component'},
        ],
        'hints': [
            'In App: `const [text, setText] = React.useState("");`',
            'Pass to children: `<MirrorInput value={text} onChange={(e) => setText(e.target.value)} />`',
            'MirrorInput simply renders: `<input value={props.value} onChange={props.onChange} />`'
        ],
        'flags': ['react_l11_flag'],
    }
)
print('  ✓ Lesson 11 + lab')

# ═══════════════════════════════════════════════════════════════════════
#  LESSON 12 — useRef Hook
# ═══════════════════════════════════════════════════════════════════════
L12_CONTENT = """## 📌 Real-World Analogy

Think of a **sticky note** on your monitor. You write something on it for your own reference — but changing that note doesn't make your entire desk rearrange itself. It's private, persistent, and doesn't disrupt anything.

**useRef** gives you a "sticky note" inside your component. It holds a value that:
- **Persists** across renders (doesn't reset)
- **Doesn't trigger a re-render** when changed (unlike state)
- Can also **point to a DOM element** directly

---

## 🧠 Two Uses of useRef

### Use 1: Accessing DOM Elements

```jsx
function FocusInput() {
  const inputRef = useRef(null);

  function handleClick() {
    inputRef.current.focus(); // Directly manipulate the DOM!
  }

  return (
    <div>
      <input ref={inputRef} placeholder="Click the button to focus me" />
      <button onClick={handleClick}>Focus Input</button>
    </div>
  );
}
```

`inputRef.current` gives you the actual DOM `<input>` element — you can call `.focus()`, `.scrollIntoView()`, etc.

### Use 2: Storing Mutable Values (without re-rendering)

```jsx
function StopWatch() {
  const [seconds, setSeconds] = useState(0);
  const intervalRef = useRef(null);

  function start() {
    intervalRef.current = setInterval(() => {
      setSeconds(s => s + 1);
    }, 1000);
  }

  function stop() {
    clearInterval(intervalRef.current);
  }

  return (
    <div>
      <p>{seconds}s</p>
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
    </div>
  );
}
```

Why useRef here? Because we need to **remember** the interval ID across renders, but we **don't want changing it to cause a re-render**.

---

## 💻 useRef vs useState

| Feature | useState | useRef |
|---------|----------|--------|
| Triggers re-render? | ✅ Yes | ❌ No |
| Persists across renders? | ✅ Yes | ✅ Yes |
| Use for UI display? | ✅ Yes | ❌ No |
| Access DOM elements? | ❌ No | ✅ Yes |

### Rule of thumb:
- Need to **display** the value on screen? → `useState`
- Need to **remember** a value silently? → `useRef`
- Need to **touch a DOM element**? → `useRef`

---

## 💻 Counting Renders (without infinite loops)

```jsx
function RenderCounter() {
  const [name, setName] = useState("");
  const renderCount = useRef(0);

  // This runs after every render
  useEffect(() => {
    renderCount.current += 1;
  });

  return (
    <div>
      <input value={name} onChange={e => setName(e.target.value)} />
      <p>This component rendered {renderCount.current} times</p>
    </div>
  );
}
```

If you used `useState` for the render count, updating it would cause another render → infinite loop! 💥

---

## 🔑 Key Takeaways

- `useRef` returns `{ current: initialValue }` — a mutable container
- Changing `.current` does NOT trigger a re-render
- Use it to access DOM elements via the `ref` attribute
- Use it to store mutable values that don't affect the UI
- Perfect for timers, previous values, render counts, and DOM manipulation
"""

les12, _ = Lesson.objects.get_or_create(
    module=mod3, slug='useref-hook',
    defaults={
        'title': 'useRef Hook',
        'content': L12_CONTENT,
        'content_type': 'text',
        'order': 4,
        'xp_reward': 25,
        'estimated_duration': 13,
    }
)

q12, _ = Quiz.objects.get_or_create(lesson=les12, defaults={
    'title': 'useRef — Quick Check',
    'passing_score': 70, 'max_attempts': 3, 'time_limit': 5,
})
qq12a, _ = QuizQuestion.objects.get_or_create(quiz=q12, order=1, defaults={
    'question_text': 'Does changing a useRef value trigger a re-render?',
    'question_type': 'single',
    'explanation': 'Unlike useState, changing a useRef value does NOT cause the component to re-render.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq12a, order=1, defaults={'answer_text': 'Yes, always', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq12a, order=2, defaults={'answer_text': 'No, it does not', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq12a, order=3, defaults={'answer_text': 'Only if the value is a number', 'is_correct': False})

qq12b, _ = QuizQuestion.objects.get_or_create(quiz=q12, order=2, defaults={
    'question_text': 'How do you access a DOM element using useRef?',
    'question_type': 'single',
    'explanation': 'You create a ref with useRef, attach it to an element with the ref attribute, and access the element via .current.',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq12b, order=1, defaults={'answer_text': 'document.getElementById()', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq12b, order=2, defaults={'answer_text': 'Attach ref to element, then use ref.current', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq12b, order=3, defaults={'answer_text': 'Use querySelector inside useEffect', 'is_correct': False})

qq12c, _ = QuizQuestion.objects.get_or_create(quiz=q12, order=3, defaults={
    'question_text': 'Why would using useState for a render counter cause an infinite loop?',
    'question_type': 'single',
    'explanation': 'Updating state causes a re-render, which updates the counter, which causes another re-render — infinite loop!',
    'points': 1,
})
QuizAnswer.objects.get_or_create(question=qq12c, order=1, defaults={'answer_text': 'Because setState is asynchronous', 'is_correct': False})
QuizAnswer.objects.get_or_create(question=qq12c, order=2, defaults={'answer_text': 'Updating state triggers a re-render, which updates it again endlessly', 'is_correct': True})
QuizAnswer.objects.get_or_create(question=qq12c, order=3, defaults={'answer_text': 'useState cannot store numbers', 'is_correct': False})

print('  ✓ Lesson 12 + quiz')

l12_lab, _ = Lab.objects.get_or_create(
    lesson=les12,
    defaults={
        'title': 'Auto-Focus Input',
        'description': 'Use useRef to automatically focus an input field when the component loads.',
        'instructions': '1. Create an AutoFocus component.\\n2. Create a ref with useRef and attach it to an `<input>` element.\\n3. Use useEffect to call `.focus()` on the input when the component mounts.\\n4. Add a "Reset Focus" button that re-focuses the input when clicked.',
        'difficulty': 'easy',
        'xp_reward': 25,
        'objectives': [
            {'type': 'frontend_code', 'contains': 'useRef', 'description': 'Use the useRef hook'},
            {'type': 'frontend_code', 'contains': '.current', 'description': 'Access the .current property'},
            {'type': 'frontend_code', 'contains': 'ref=', 'description': 'Attach the ref to an element'},
        ],
        'hints': [
            'Create the ref: `const inputRef = React.useRef(null);`',
            'Attach it: `<input ref={inputRef} placeholder="I auto-focus!" />`',
            'Focus on mount: `React.useEffect(() => { inputRef.current.focus(); }, []);`'
        ],
        'flags': ['react_l12_flag'],
    }
)
print('  ✓ Lesson 12 + lab')

# ── Done ──────────────────────────────────────────────────────────────
print('\n✅ React course Modules 1, 2 & 3 created successfully!')
print('   Course: React from Zero to Hero')
print('   Module 1: React Foundations (4 lessons)')
print('   Module 2: Interactivity & State (4 lessons)')
print('   Module 3: Data Flow & Effects (4 lessons)')
print('   Visit: /courses/react-zero-to-hero/')
