"""Force-update hints on ALL React labs (fixes labs created before hints were added)."""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from labs.models import Lab

HINTS = {
    # Module 1
    'Hello React!': [
        'Make sure you spell the function name exactly as `WelcomeMessage` with a capital W.',
        'Remember to return some JSX like `return <h1>...</h1>`.',
        'Render it using: `const root = ReactDOM.createRoot(document.getElementById("root")); root.render(<WelcomeMessage />);`'
    ],
    'Composing Components': [
        'Start by creating three separate functions: SiteHeader, SiteFooter, and App.',
        'In App, return a `<div>` that contains both `<SiteHeader />` and `<SiteFooter />`.',
        "Don't forget that all component functions must start with a capital letter!"
    ],
    'JSX Superpowers': [
        'To display the name, simply write `{name}` inside your JSX.',
        'The ternary operator looks like this: `condition ? ifTrue : ifFalse`.',
        'Example: `Status: {isOnline ? "🟢 Online" : "🔴 Offline"}`'
    ],
    'Passing Props': [
        'Your component should look like: `function StudentCard(props) { ... }` or use destructuring `({ name, grade })`.',
        'When rendering the component, pass props like attributes: `<StudentCard name="Alice" grade="A" />`.',
        'Make sure you have an `App` component that renders two separate StudentCards then renders App.'
    ],
    # Module 2
    'Build a Counter': [
        'Start with: `const [count, setCount] = React.useState(0);`',
        'Your button should look like: `<button onClick={() => setCount(count + 1)}>Increment</button>`',
        'Display the count: `<p>Count: {count}</p>`'
    ],
    'Interactive Buttons': [
        'Start with `const [color, setColor] = React.useState("none");` to track the selected color.',
        'Each button should call setColor: `<button onClick={() => setColor("Red")}>Red</button>`',
        'Display the color: `<p>Selected color: {color}</p>`'
    ],
    'Show / Hide Toggle': [
        'Start with `const [visible, setVisible] = React.useState(false);`',
        'Toggle with: `<button onClick={() => setVisible(!visible)}>Toggle</button>`',
        'Conditionally render: `{visible && <p>The secret is React rocks!</p>}`'
    ],
    'Fruit List': [
        'Define your array: `const fruits = ["Apple", "Banana", "Cherry", "Mango"];`',
        'Map over it: `{fruits.map(fruit => <li key={fruit}>{fruit}</li>)}`',
        'Wrap everything in a `<ul>` tag for proper HTML list structure.'
    ],
    # Module 3
    'Document Title Updater': [
        'Start with `const [count, setCount] = React.useState(0);`',
        'Add useEffect: `React.useEffect(() => { document.title = `Count: ${count}`; }, [count]);`',
        'Display and increment: `<button onClick={() => setCount(count + 1)}>Count: {count}</button>`'
    ],
    'Contact Form': [
        'Track two state variables: `const [name, setName] = React.useState(""); const [message, setMessage] = React.useState("");`',
        'The input should look like: `<input value={name} onChange={(e) => setName(e.target.value)} />`',
        'Add `<form onSubmit={(e) => { e.preventDefault(); alert(name + ": " + message); }}>` around your inputs.'
    ],
    'Synced Inputs': [
        'In App: `const [text, setText] = React.useState("");`',
        'Pass to children: `<MirrorInput value={text} onChange={(e) => setText(e.target.value)} />`',
        'MirrorInput simply renders: `<input value={props.value} onChange={props.onChange} />`'
    ],
    'Auto-Focus Input': [
        'Create the ref: `const inputRef = React.useRef(null);`',
        'Attach it: `<input ref={inputRef} placeholder="I auto-focus!" />`',
        'Focus on mount: `React.useEffect(() => { inputRef.current.focus(); }, []);`'
    ],
}

updated = 0
for lab in Lab.objects.filter(lesson__module__course__slug='react-zero-to-hero'):
    if lab.title in HINTS:
        lab.hints = HINTS[lab.title]
        lab.save()
        status = "✅ updated" if not lab.hints == HINTS[lab.title] else "✅ set"
        print(f"  {status}: {lab.title} → {len(HINTS[lab.title])} hints")
        updated += 1
    else:
        print(f"  ⚠️  no hints defined for: {lab.title}")

print(f"\n✅ Done! Updated {updated} labs with hints.")
