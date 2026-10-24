// Copy into a Vitest-enabled React + Ink project.
// Prerequisites: ink, react, ink-testing-library, vitest, and TSX support.
import React, {useState} from 'react';
import {Text, useInput} from 'ink';
import {render} from 'ink-testing-library';
import {expect, it, vi} from 'vitest';

type CounterProps = {initial?: number};

function Counter({initial = 0}: CounterProps) {
  const [count, setCount] = useState(initial);

  useInput(input => {
    if (input === '+') {
      setCount(value => value + 1);
    }
  });

  return <Text>Count: {count}</Text>;
}

it('renders the initial value', () => {
  const view = render(<Counter initial={2} />);
  try {
    expect(view.lastFrame()).toBe('Count: 2');
  } finally {
    view.unmount();
    view.cleanup();
  }
});

it('handles terminal keyboard input', async () => {
  const view = render(<Counter />);
  try {
    expect(view.lastFrame()).toBe('Count: 0');
    view.stdin.write('+');
    await vi.waitFor(() => {
      expect(view.lastFrame()).toBe('Count: 1');
    });
    expect(view.frames.some(frame => frame.includes('Count: 0'))).toBe(true);
    expect(view.frames.some(frame => frame.includes('Count: 1'))).toBe(true);
  } finally {
    view.unmount();
    view.cleanup();
  }
});
