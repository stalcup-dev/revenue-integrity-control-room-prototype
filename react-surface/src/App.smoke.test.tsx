import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import App from './App'

describe('Route persistence and operational slices', () => {
  it('persists global filters when navigating to Charge Reconciliation', async () => {
    render(<App />)
    const user = userEvent.setup()

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(departmentSelect, 'Radiology / Interventional Radiology')
    await user.click(screen.getByRole('link', { name: /charge reconciliation/i }))

    expect(screen.getByText(/charge reconciliation monitor/i)).toBeInTheDocument()

    const [departmentSelectOnReconciliation] = screen.getAllByLabelText(/department/i)
    expect(departmentSelectOnReconciliation).toHaveValue('Radiology / Interventional Radiology')
    expect(getMetricCardValue('Reconciliation cases')).toBe('2')
  })

  it('recalculates reconciliation KPIs when filters change', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /charge reconciliation/i }))

    expect(getMetricCardValue('Reconciliation cases')).toBe('5')
    expect(getMetricCardValue('Late-charge pressure')).toBe('$80,100')

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(
      departmentSelect,
      'OR / Hospital Outpatient Surgery / Procedural Areas',
    )

    expect(getMetricCardValue('Reconciliation cases')).toBe('2')
    expect(getMetricCardValue('Late-charge pressure')).toBe('$52,150')
  })

  it('persists global filters when navigating to Prebill Holds', async () => {
    render(<App />)
    const user = userEvent.setup()

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(departmentSelect, 'Radiology / Interventional Radiology')
    await user.click(screen.getByRole('link', { name: /prebill holds/i }))

    expect(screen.getByText(/modifiers \/ edits \/ prebill holds/i)).toBeInTheDocument()

    const [departmentSelectOnPrebill] = screen.getAllByLabelText(/department/i)
    expect(departmentSelectOnPrebill).toHaveValue('Radiology / Interventional Radiology')
    expect(getMetricCardValue('Active prebill holds')).toBe('1')
  })

  it('recalculates prebill KPIs when filters change', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /prebill holds/i }))

    expect(getMetricCardValue('Active prebill holds')).toBe('2')
    expect(getMetricCardValue('Dollars held pre-final bill')).toBe('$40,200')

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(
      departmentSelect,
      'OR / Hospital Outpatient Surgery / Procedural Areas',
    )

    expect(getMetricCardValue('Active prebill holds')).toBe('1')
    expect(getMetricCardValue('Dollars held pre-final bill')).toBe('$28,450')
  })

  it('persists global filters when navigating to Documentation Exceptions', async () => {
    render(<App />)
    const user = userEvent.setup()

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(departmentSelect, 'Radiology / Interventional Radiology')
    await user.click(screen.getByRole('link', { name: /documentation exceptions/i }))

    expect(screen.getByText(/documentation support exceptions/i)).toBeInTheDocument()

    const [departmentSelectOnDocumentation] = screen.getAllByLabelText(/department/i)
    expect(departmentSelectOnDocumentation).toHaveValue(
      'Radiology / Interventional Radiology',
    )
    expect(getMetricCardValue('Documentation exception cases')).toBe('1')
  })

  it('recalculates documentation KPIs when filters change', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /documentation exceptions/i }))

    expect(getMetricCardValue('Documentation exception cases')).toBe('2')
    expect(getMetricCardValue('Post-window documentation loss')).toBe('$7,600')

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(departmentSelect, 'Outpatient Infusion / Oncology Infusion')

    expect(getMetricCardValue('Documentation exception cases')).toBe('1')
    expect(getMetricCardValue('Post-window documentation loss')).toBe('$0')
  })
})

function getMetricCardValue(label: string): string {
  const labelNode = screen.getByText(label)
  const card = labelNode.closest('article')

  if (!card) {
    throw new Error(`Metric card for "${label}" was not found.`)
  }

  const valueNode = within(card).getByText((_, element) => {
    if (element?.tagName !== 'P') {
      return false
    }

    return (
      element.className.includes('text-3xl') || element.className.includes('text-2xl')
    )
  })

  return valueNode.textContent?.trim() ?? ''
}
