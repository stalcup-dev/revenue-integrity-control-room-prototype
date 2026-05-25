import axe from 'axe-core'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import App from './App'

async function runAxe(container: HTMLElement) {
  return axe.run(container, {
    rules: {
      // JSDOM cannot compute real visual contrast in the same way as browsers.
      'color-contrast': { enabled: false },
    },
  })
}

describe('Accessibility smoke checks', () => {
  it('has no critical accessibility violations on Control Room Summary', async () => {
    const { container } = render(<App />)

    expect(
      await screen.findByText(
        /which outpatient queues should leadership work first to reduce recoverable revenue leakage and compliance risk/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Action Tracker route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /action tracker/i }))

    expect(
      await screen.findByText(
        /which interventions should leadership hold, expand, or revise to reduce queue pressure and protect recoverable dollars/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Prebill Holds route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /prebill holds/i }))

    expect(
      await screen.findByText(/modifiers \/ edits \/ prebill holds/i),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Scenario Lab route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /scenario lab/i }))

    expect(
      await screen.findByText(
        /which operational lever shift has the strongest bounded impact on recoverable dollars, backlog reduction, and sla improvement/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Denial Feedback + CDM Governance route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /denial feedback \+ cdm governance/i }))

    expect(
      await screen.findByText(
        /which downstream denial patterns point to upstream cdm or rule governance gaps that leadership should remediate next/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Documentation Trend Realism route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /documentation trend realism/i }))

    expect(
      await screen.findByText(
        /is documentation queue movement behaving like real operational entry\/exit flow, or are we showing a cosmetically flat trend/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Queue Governance Browser route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /queue governance browser/i }))

    expect(
      await screen.findByText(
        /which queue stages are absorbing recoverable opportunity, where are sla thresholds breached, and who owns escalation now/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Page Storytelling Validation route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /page storytelling validation/i }))

    expect(
      await screen.findByText(
        /do non-summary work pages consistently answer what control is monitored, where pressure sits, and who owns the next move/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Trust Dent Remediation route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /trust dent remediation/i }))

    expect(
      await screen.findByText(
        /have the highest-risk reviewer trust dents been remediated with explicit evidence and no-build-boundary discipline/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Decision Pack Freshness Lens route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /decision pack freshness lens/i }))

    expect(
      await screen.findByText(
        /is the decision pack being read as a current deterministic snapshot, or as stale validation proof/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Reviewer Proof Pack Lens route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /reviewer proof pack lens/i }))

    expect(
      await screen.findByText(
        /are reviewer claims anchored to the strongest proof path first, with supporting artifacts clearly separated from core evidence/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })

  it('has no critical accessibility violations on Scenario Claim-Tightening Lens route', async () => {
    const { container } = render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('link', { name: /scenario claim-tightening lens/i }))

    expect(
      await screen.findByText(
        /is scenario lab messaging staying in deterministic what-if bounds, with explicit proof and caveats for skeptical reviewers/i,
      ),
    ).toBeInTheDocument()

    const results = await runAxe(container)

    expect(results.violations).toHaveLength(0)
  })
})
