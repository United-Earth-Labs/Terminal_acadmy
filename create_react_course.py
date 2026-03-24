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

# ── Done ──────────────────────────────────────────────────────────────
print('\n✅ React course Module 1 created successfully!')
print('   Course: React from Zero to Hero')
print('   Module: React Foundations (4 lessons + quizzes)')
print('   Visit: /courses/react-zero-to-hero/')
