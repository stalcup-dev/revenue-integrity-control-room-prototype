import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import App from './App'

describe('Route persistence and operational slices', () => {
  it('persists global filters when navigating to Charge Reconciliation', async () => {
    render(<App />)
    const user = userEvent.setup()

    expect(await screen.findByText(/department pressure view/i)).toBeInTheDocument()
    expect(screen.getByText(/representative deterministic proof/i)).toBeInTheDocument()
    expect(screen.getByText(/featured deterministic story/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /focus featured case/i }))

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(departmentSelect, 'Radiology / Interventional Radiology')
    await user.click(screen.getByRole('link', { name: /charge reconciliation/i }))

    expect(await screen.findByText(/charge reconciliation monitor/i)).toBeInTheDocument()

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

    expect(await screen.findByText(/modifiers \/ edits \/ prebill holds/i)).toBeInTheDocument()

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

    expect(await screen.findByText(/documentation support exceptions/i)).toBeInTheDocument()

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

  it('renders Action Tracker and updates intervention metrics from local filters', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /action tracker/i }))

    expect(await screen.findByText(/opportunity and action tracker/i)).toBeInTheDocument()
    expect(getMetricCardValue('Total interventions')).toBe('4')
    expect(getMetricCardValue('Needs revision')).toBe('1')

    await user.click(
      screen.getByRole('button', {
        name: /view impacted cases for ir interface retry guardrail/i,
      }),
    )

    expect(await screen.findByText(/impacted case worklist/i)).toBeInTheDocument()
    expect(getMetricCardValue('Impacted cases')).toBe('2')
    expect(screen.getAllByText('RI-IR-0031').length).toBeGreaterThan(0)

    await user.selectOptions(screen.getByLabelText(/checkpoint status/i), 'Needs revision')

    expect(getMetricCardValue('Total interventions')).toBe('1')
    expect(getMetricCardValue('Needs revision')).toBe('1')

    await user.selectOptions(screen.getByLabelText(/checkpoint status/i), 'All')
    await user.selectOptions(screen.getByLabelText(/recommendation/i), 'Revise')

    expect(getMetricCardValue('Total interventions')).toBe('2')
    expect(getMetricCardValue('Not started')).toBe('1')
  })

  it('renders Scenario Lab and recalculates projected metrics when lever targets change', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /scenario lab/i }))

    expect(
      await screen.findByText(
        /which operational lever shift has the strongest bounded impact on recoverable dollars, backlog reduction, and sla improvement/i,
      ),
    ).toBeInTheDocument()

    const initialLift = getMetricCardValue('Projected recoverable dollar lift')

    const clearanceTargetInput = screen.getByLabelText(/prebill edit clearance rate target/i)
    await user.clear(clearanceTargetInput)
    await user.type(clearanceTargetInput, '95')

    const updatedLift = getMetricCardValue('Projected recoverable dollar lift')
    expect(updatedLift).not.toBe(initialLift)
  })

  it('persists global filters when navigating to Denial Feedback + CDM Governance', async () => {
    render(<App />)
    const user = userEvent.setup()

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(departmentSelect, 'OR / Hospital Outpatient Surgery / Procedural Areas')
    await user.click(screen.getByRole('link', { name: /denial feedback \+ cdm governance/i }))

    expect(
      await screen.findByText(
        /which downstream denial patterns point to upstream cdm or rule governance gaps that leadership should remediate next/i,
      ),
    ).toBeInTheDocument()

    const [departmentSelectOnMonitor] = screen.getAllByLabelText(/department/i)
    expect(departmentSelectOnMonitor).toHaveValue('OR / Hospital Outpatient Surgery / Procedural Areas')
    expect(getMetricCardValue('Downstream denial signals')).toBe('4')
  })

  it('recomputes documentation trend realism metrics when department filter changes', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /documentation trend realism/i }))

    expect(
      await screen.findByText(
        /is documentation queue movement behaving like real operational entry\/exit flow, or are we showing a cosmetically flat trend/i,
      ),
    ).toBeInTheDocument()

    expect(getMetricCardValue('Current backlog')).toBe('7')
    expect(getMetricCardValue('Current documentation dollars open')).toBe('$4,310')

    const [departmentSelect] = screen.getAllByLabelText(/department/i)
    await user.selectOptions(departmentSelect, 'Radiology / Interventional Radiology')

    expect(getMetricCardValue('Current backlog')).toBe('3')
    expect(getMetricCardValue('Current documentation dollars open')).toBe('$1,360')
  })

  it('renders Queue Governance Browser and recalculates governed counts from local filters', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /queue governance browser/i }))

    expect(
      await screen.findByText(
        /which queue stages are absorbing recoverable opportunity, where are sla thresholds breached, and who owns escalation now/i,
      ),
    ).toBeInTheDocument()

    expect(getMetricCardValue('Governed active items')).toBe('9')

    await user.selectOptions(screen.getByLabelText(/queue stage/i), 'Documentation pending')

    expect(getMetricCardValue('Governed active items')).toBe('1')
  })

  it('renders Page Storytelling Validation and shows expected cue coverage', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /page storytelling validation/i }))

    expect(
      await screen.findByText(
        /do non-summary work pages consistently answer what control is monitored, where pressure sits, and who owns the next move/i,
      ),
    ).toBeInTheDocument()

    expect(getMetricCardValue('Pages validated')).toBe('5')
    expect(getMetricCardValue('Full-cue pages')).toBe('4')
    expect(getMetricCardValue('Thin-cue pages')).toBe('1')
  })

  it('renders Trust Dent Remediation and shows remediated packaging ledger state', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /trust dent remediation/i }))

    expect(
      await screen.findByText(
        /have the highest-risk reviewer trust dents been remediated with explicit evidence and no-build-boundary discipline/i,
      ),
    ).toBeInTheDocument()

    expect(getMetricCardValue('Trust dents tracked')).toBe('4')
    expect(getMetricCardValue('Remediated')).toBe('4')
    expect(getMetricCardValue('Watchlist')).toBe('0')
  })

  it('renders Decision Pack Freshness Lens with current-snapshot framing', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /decision pack freshness lens/i }))

    expect(
      await screen.findByText(
        /is the decision pack being read as a current deterministic snapshot, or as stale validation proof/i,
      ),
    ).toBeInTheDocument()

    expect(getMetricCardValue('Total open exceptions')).toBe('9')
    expect(getMetricCardValue('Exceptions breaching SLA')).toBe('4')
    expect(getMetricCardValue('Top owner queue in the current slice')).toBe(
      'Prebill edit / hold',
    )
  })

  it('renders Reviewer Proof Pack Lens with core-first proof inventory', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /reviewer proof pack lens/i }))

    expect(
      await screen.findByText(
        /are reviewer claims anchored to the strongest proof path first, with supporting artifacts clearly separated from core evidence/i,
      ),
    ).toBeInTheDocument()

    expect(getMetricCardValue('Proof assets')).toBe('10')
    expect(getMetricCardValue('Core proof')).toBe('5')
    expect(getMetricCardValue('Supporting proof')).toBe('5')
  })

  it('renders Scenario Claim-Tightening Lens with bounded claim inventory', async () => {
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /scenario claim-tightening lens/i }))

    expect(
      await screen.findByText(
        /is scenario lab messaging staying in deterministic what-if bounds, with explicit proof and caveats for skeptical reviewers/i,
      ),
    ).toBeInTheDocument()

    expect(getMetricCardValue('Scenario claims tracked')).toBe('3')
    expect(getMetricCardValue('Low-risk claims')).toBe('2')
    expect(getMetricCardValue('Moderate-risk claims')).toBe('1')
  })
})

function getMetricCardValue(label: string): string {
  const labelCandidates = screen.getAllByText((text) => text.trim() === label)

  for (const labelNode of labelCandidates) {
    const card = labelNode.closest('article')

    if (!card) {
      continue
    }

    const valueNode = within(card).queryByText((_, element) => {
      if (element?.tagName !== 'P') {
        return false
      }

      return (
        element.className.includes('text-3xl') || element.className.includes('text-2xl')
      )
    })

    if (valueNode) {
      return valueNode.textContent?.trim() ?? ''
    }
  }

  throw new Error(`Metric card for "${label}" was not found.`)
}
