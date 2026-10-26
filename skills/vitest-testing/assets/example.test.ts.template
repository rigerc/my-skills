// Adapt './add' to a real module in your project.
import { expect, test } from 'vitest'
import { add } from './add'

test.for([
  { a: 1, b: 2, result: 3 },
  { a: -1, b: 1, result: 0 },
])('add($a, $b) returns $result', ({ a, b, result }) => {
  expect(add(a, b)).toBe(result)
})
