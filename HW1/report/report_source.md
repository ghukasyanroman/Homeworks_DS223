# Bass model analysis of Posha

Roman Ghukasyan | Marketing Analytics | October 19, 2026

## 1. Chosen innovation

I chose Posha from TIME's Best Inventions of 2025. It is a kitchen robot that cooks one-pot meals. The user prepares and loads the ingredients, then Posha adds them, stirs and uses a camera to adjust the cooking [R1, R2]. I found it interesting because it could help people who want home-cooked food but do not have much time to stand next to the stove.

## 2. Look-alike innovation: the countertop microwave

I chose the microwave because both products bring a different way of preparing food into the home. Both take kitchen space, cost money and help reduce the time or attention needed for cooking. For either product, seeing another household use it could make the benefits easier to understand. BLS reports that the countertop microwave was introduced in 1967 [R5].

The technologies are different. A microwave heats food, while Posha automates several cooking steps. Also, the microwave data covers a whole category and Posha is one brand. So I use microwave diffusion as a starting comparison and estimate a much smaller market for Posha. I do not expect the two products to reach the same level of ownership.

## 3. Historical data

I use U.S. microwave ownership from EIA Table 2.6 [R3]. There are 12 usable observations from 1978 to 2009. I leave the missing 1979 entry out of estimation and keep the actual survey years, without filling the gaps. The original table and extracted CSV are in data/.

Ownership is a proxy for cumulative adoption, not a direct count of first purchases. I fit ownership shares so growth in the number of households does not get mixed with diffusion. To express historical M in household units, I use the fixed 1978 base of 77 million households [R3]. These are standardized household equivalents, not actual unique buyers. The small fall in ownership from 1993 to 1997 stays in the data because these are rounded survey estimates.

| Year | Microwave ownership |
| --- | --- |
| 1978 | 8% |
| 1979 | NA |
| 1980 | 14% |
| 1981 | 17% |
| 1982 | 21% |
| 1984 | 34% |
| 1987 | 61% |
| 1990 | 79% |
| 1993 | 84% |
| 1997 | 83% |
| 2001 | 86% |
| 2005 | 88% |
| 2009 | 96% |

<!-- pagebreak -->

## 4. Estimate p, q and M

I use the cumulative Bass model [R6]:

N(t) = M * (1 - exp(-(p+q)*t)) / (1 + (q/p)*exp(-(p+q)*t))

Here p describes external influence, q describes imitation, M is market potential and N(t) is cumulative adoption. Time is measured in years from 1967. I estimate p, q and the ownership ceiling together with nonlinear least squares, giving each survey the same weight. The ceiling is restricted to between 50% and 100%. The helper tries several starting values, and none of the fitted parameters is at a bound.


| Parameter | Estimate |
| --- | --- |
| p | 0.00050491 per year |
| q | 0.36524560 per year |
| Historical M, fixed 1978 base | 68.52 million household equivalents |
| Equivalent ownership ceiling | 88.98% |

![Observed microwave ownership and fitted curve](../img/microwave_fit.png)

The fit has R-squared = 0.9921 and RMSE = 2.91 percentage points. It follows the main rise but levels off near 89%, below the final observed 96%. These are fit measures, not evidence that the Posha forecast is accurate.

## 5. Predict Posha's diffusion

I use the estimated microwave p and q as an assumption for Posha. These rates are not fitted to Posha sales. I estimate a separate market because a premium robot from one company is different from the whole microwave market.

Census reports 132,737,146 U.S. households in 2024 [R4]. Posha lists a regular price of $1,750 [R2], so I treat it as a premium purchase. Using Fermi logic, I assume 20% of households could afford it, have suitable space and want cooking help. I then assume 2.5% of this group eventually chooses Posha. Both percentages are my assumptions, not survey results.

M = 132,737,146 * 0.20 * 0.025 = 663,685.73 households

This is about 664,000 households, or 0.5% of all U.S. households. The manufacturer's page says Posha is in 1,000+ homes [R2]. I use exactly 1,000 as a planning starting value at the beginning of 2027. This is not an observed end-of-2026 total. The forecast starts from these households rather than restarting adoption from zero. I keep the household base and market potential fixed.

<!-- pagebreak -->

## 6. Scope: United States

I chose the U.S. because Posha currently ships there [R2] and the microwave data also covers U.S. households [R3]. This keeps the same country for both products. I count households because several people can share one appliance. One household is counted once, and replacement purchases are not additional adopters.


## 7. Adopters by year

The forecast covers the end of each year from 2027 to 2046. Cumulative adoption includes the starting 1,000 households. New adopters in a year are N(t) - N(t-1), not the instantaneous adoption rate. I calculate with unrounded values and round only for display. The full-precision results are saved in data/posha_forecast.csv.


| Year | New households | Cumulative households |
| --- | --- | --- |
| 2027 | 843 | 1,843 |
| 2028 | 1,212 | 3,055 |
| 2029 | 1,739 | 4,794 |
| 2030 | 2,491 | 7,285 |
| 2031 | 3,558 | 10,844 |
| 2032 | 5,062 | 15,906 |
| 2033 | 7,161 | 23,067 |
| 2034 | 10,049 | 33,116 |
| 2035 | 13,944 | 47,060 |
| 2036 | 19,050 | 66,109 |
| 2037 | 25,479 | 91,588 |
| 2038 | 33,128 | 124,716 |
| 2039 | 41,525 | 166,242 |
| 2040 | 49,727 | 215,969 |
| 2041 | 56,394 | 272,363 |
| 2042 | 60,137 | 332,500 |
| 2043 | 60,064 | 392,564 |
| 2044 | 56,193 | 448,757 |
| 2045 | 49,444 | 498,201 |
| 2046 | 41,213 | 539,414 |

![Posha cumulative adoption and new households each year](../img/posha_forecast.png)

<!-- pagebreak -->

## What I understand from the results

The forecast reaches about 7,300 households by 2030 and 47,100 by 2035. By 2046 it reaches about 539,400, still below the assumed market potential. The largest annual addition is around 2042, at about 60,100 households.

Growth starts slowly because p is small. Later, imitation becomes more important in the model. Eventually fewer households remain in the market and annual adoption falls. This explains the S-shaped cumulative curve and the rise and fall in new adopters. It does not prove that word of mouth caused the historical growth.

The main limits are the ownership proxy, comparing a product category with one brand, and the assumed Posha market shares. The historical curve also levels off below the last ownership observation. Price changes, competition, supply limits and household growth are not included. The forecast assumes Posha continues as a product line over these years. I would use it as a possible scenario and update it when actual customer data becomes available.


## References

[R1] Barker Bonomo, E. (2025, October 9). Posha: Robotic home chef. TIME, Best Inventions of 2025. [TIME entry](https://time.com/collections/best-inventions-2025/7318336/posha/).

[R2] Posha. (n.d.). How Posha works. [Manufacturer page](https://www.posha.com/how-posha-works). Accessed October 19, 2026. Source for product features, U.S. shipping, regular price of $1,750 and the statement that Posha is in 1,000+ homes. Prices and availability can change.

[R3] U.S. Energy Information Administration. (2012). Annual Energy Review 2011, Table 2.6: Household end uses, selected years, 1978-2009. [Historical data](https://www.eia.gov/totalenergy/data/annual/showtext.php?t=ptb0206). Source for microwave ownership and household totals. The original table is saved in data/.

[R4] U.S. Census Bureau. (2025). 2024 American Community Survey, 1-Year Estimates, S1101: Households and families, United States. [Census table](https://data.census.gov/table/ACSST1Y2024.S1101). Total households: 132,737,146.

[R5] Liegey, P. R. (2000). Hedonic quality adjustment methods for microwave ovens in the U.S. CPI. U.S. Bureau of Labor Statistics. [BLS article](https://www.bls.gov/cpi/quality-adjustment/microwave-ovens.htm). Source for the 1967 introduction of the countertop microwave.

[R6] Bass, F. M. (1969). A new product growth for model consumer durables. Management Science, 15(5), 215-227. [Original paper](https://doi.org/10.1287/mnsc.15.5.215).

The 20% eligible share, 2.5% Posha take-up share and exact starting count of 1,000 households are my assumptions. They are not measured market shares or a dated customer total. Sources accessed October 19, 2026.
