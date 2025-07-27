# TIGRO Portfolio Optimization Logic - Two-Phase Approach

## 🎯 **STRATEGIC FRAMEWORK**

### **Core Investment Philosophy**
- **Target Return**: ~10-12% annually  
- **Cash Constraint**: Maximum $10,000 net new investment
- **Sector Limits**: 40% maximum per sector [[memory:4445823]]
- **Strategy Order**: SELL → TRIM → BUY NEW → TOP UP positive return stocks

### **Critical Insight: Markowitz vs Strategic Constraints**
The optimal Markowitz solution may conflict with our strategic order. **Solution: Two-Phase Optimization**

---

## 🔄 **TWO-PHASE OPTIMIZATION APPROACH**

### **Phase 1: Pure Markowitz Optimization**
```
Purpose: Find mathematically optimal portfolio allocation
Input: 150+ universe stocks + current portfolio  
Constraints: Standard Markowitz (risk, return, sector limits)
Output: Optimal weights without strategic constraints
```

### **Phase 2: Strategic Adjustment**
```
Purpose: Adjust Phase 1 solution to respect strategic order
Process:
1. Compare Phase 1 vs current portfolio
2. Classify actions by strategic priority:
   - SELL: Underperformers, negative sentiment
   - TRIM: Overweight positions, profit-taking
   - BUY NEW: Fresh opportunities from universe
   - TOP UP: Positive return stocks (backup only)
3. Re-optimize within strategic constraints
4. Validate total cash usage ≤ $10,000
```

---

## 📊 **POSITION CLASSIFICATION LOGIC**

### **Action Determination**
```python
# Fixed floating-point precision bug
effective_target = target_shares if abs(target_shares) > 1e-10 else 0.0

if effective_target < current_shares * 0.1:  # 90%+ reduction
    action = 'SELL'
elif current_return > 0 and shares_change > 0:  # Adding to profitable position
    action = 'TOP_UP_BACKUP'  # Lower priority
else:
    action = 'TRIM' or 'ADD' based on magnitude
```

### **Positive Return Constraint**
- Stocks with `current_return > 0` → Backup pool only
- Used only if budget remains after primary strategy
- Prevents buying winners at premium prices

---

## 🔍 **SUPERVISOR QUALITY CONTROLS**

### **Section-by-Section Validation**
Each section requires **Senior Portfolio Manager** approval:

1. **Data Integrity**: All values computed, no hardcoding
2. **Mathematical Validation**: Returns, volatility, correlations reasonable  
3. **Strategic Compliance**: Order respected, constraints met
4. **Risk Assessment**: VaR, sector concentration, stop losses
5. **Cash Flow Logic**: Net investment ≤ $10,000, realistic execution
6. **Real Money Perspective**: Would I invest my own money based on this?

---

## 🚀 **EXECUTION SECTIONS**

### **Section 1: Data Collection & Validation**
- Load 150+ universe stocks from `master name ticker.csv`
- Validate current portfolio from `actual-portfolio-master.csv`  
- Cross-reference sentiment data
- **Supervisor Check**: Data completeness and quality

### **Section 2: Phase 1 Optimization**
- Pure Markowitz optimization (no strategic constraints)
- Calculate optimal weights for entire universe
- **Supervisor Check**: Mathematical reasonableness

### **Section 3: Strategic Analysis** 
- Compare optimal vs current positions
- Classify actions by strategic priority
- Identify conflicts between phases
- **Supervisor Check**: Strategic logic sound

### **Section 4: Phase 2 Adjustment**
- Re-optimize respecting strategic order
- Apply positive return backup constraint
- Validate cash usage within limits
- **Supervisor Check**: Final recommendations viable

### **Section 5: Risk & Execution Validation**
- Calculate VaR, stop losses, sector exposure
- Generate execution timeline
- Final sanity checks
- **Supervisor Check**: Ready for real money deployment

---

## 🛡️ **CRITICAL SAFEGUARDS**

### **No Hardcoded Values**
- All HTML dynamically generated from computed data
- Supervisor must verify no static values in output
- Timestamps show real computation time

### **Real Money Validation**
- Each recommendation must pass "would I invest my own money?" test
- Conservative bias when uncertain
- Clear rationale for every position change

### **Fresh Perspective Protocol**
- Supervisor acts with no memory of previous discussions
- Questions everything as if seeing for first time
- Independent validation of all logic and calculations

---

## 📋 **IMPLEMENTATION CHECKLIST**

- [ ] **Two-phase optimizer implemented**
- [ ] **Strategic order enforcement coded**  
- [ ] **Positive return backup logic active**
- [ ] **Floating-point precision bugs fixed**
- [ ] **150+ universe stock access verified**
- [ ] **Supervisor checkpoints programmed**
- [ ] **No hardcoded HTML values confirmed**
- [ ] **Real money deployment readiness validated**

---

*This document serves as the definitive guide for portfolio optimization logic. All deviations must be documented and approved by the supervisor role.* 