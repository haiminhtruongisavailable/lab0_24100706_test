# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge


def count_val(dut):
    return int(dut.uo_out.value) & 0xF


async def settle(dut):
    # Sample after falling edge so RTL and gate-level both see a stable Q.
    await FallingEdge(dut.clk)


@cocotb.test()
async def test_project(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    await settle(dut)
    assert count_val(dut) == 0, "reset must force count=0"

    dut.rst_n.value = 1
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 4)
    await settle(dut)
    assert count_val(dut) == 0, "en=0 must hold 0"

    dut.ui_in.value = 1
    await ClockCycles(dut.clk, 5)
    await settle(dut)
    assert count_val(dut) == 5, "five enabled clocks -> 5"

    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 3)
    await settle(dut)
    assert count_val(dut) == 5, "en=0 must hold 5"

    dut.ui_in.value = 1
    await ClockCycles(dut.clk, 10)
    await settle(dut)
    assert count_val(dut) == 15, "count to 15"

    await ClockCycles(dut.clk, 1)
    await settle(dut)
    assert count_val(dut) == 0, "15+1 wraps to 0"
